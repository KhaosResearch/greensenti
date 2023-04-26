from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pyproj
import rasterio
from matplotlib import pyplot as plt
from rasterio import mask
from rasterio.plot import adjust_band, reshape_as_image, reshape_as_raster
from rasterio.warp import Resampling, reproject
from sentinelsat import read_geojson
from shapely.geometry import Polygon, shape
from shapely.ops import transform


def crop_by_shape(filename: Path, geom: Polygon, output: str, override_no_data: float | None = None) -> None:
    """
    Crop input file with a polygon mask.

    :param filename: Path to input image.
    :param geom: Geometry in GeoJSON format.
    :param output: Path to output file.
    :param override_no_data: Value to fill outside the crop area. Useful to separate no data of fill. Raises `ValueError` if this value is present in the raster.
    """
    with rasterio.open(filename) as src:
        assert override_no_data not in src.read(), f"Value {override_no_data} is present in the raster."
        out_image, out_transform = mask.mask(src, shapes=[geom], crop=True, nodata=override_no_data)
    out_meta = src.meta.copy()
    out_meta.update(
        {"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform}
    )
    with rasterio.open(output, "w", **out_meta) as dest:
        dest.write(out_image)


def project_shape(geom: Polygon, scs: str = "epsg:4326", dcs: str = "epsg:32630") -> Polygon:
    """
    Project a shape from a source coordinate system to another one.
    The source coordinate system can be obtained with `rasterio` as illustrated next:

    >>> import rasterio
    >>> print(rasterio.open('example.jp2').crs)

    This is useful when the geometry has its points in "normal" coordinate reference systems while the geoTiff/jp2 data
    is expressed in other coordinate system.

    :param geom: Geometry, e.g., {'type': 'Polygon', 'coordinates': [[(1,2), (3,4), (5,6), (7,8), (9,10)]]}
    :param scs: Source reference coordinate system.
    :param dcs: Destination reference coordinate system.
    :return: Geometry in destination coordinate system.
    """
    init_crs = pyproj.CRS(scs)
    final_crs = pyproj.CRS(dcs)
    project = pyproj.Transformer.from_crs(init_crs, final_crs, always_xy=True).transform
    return transform(project, shape(geom))


def save_as_img(raster: np.ndarray, output: Path, **kwargs) -> None:
    """
    Save raster image to file.
    :param raster: Source raster image.
    :param output: Path to output file.
    :param kwargs: Additional arguments to pass to `matplotlib.pyplot.imshow`.
    """
    fig, ax = plt.subplots(figsize=plt.figaspect(raster), frameon=False)
    fig.subplots_adjust(0, 0, 1, 1)

    ax.imshow(raster, **kwargs)
    fig.savefig(output, dpi=300, transparent=True)
    plt.close(fig)


def transform_image(band: Path, color_map: Optional[str], output: Path) -> None:
    """
    Transform raster to image. See full list of accepted drivers at https://gdal.org/drivers/raster/index.html.

    :param band: TIF band image.
    :param color_map: Color map to use.
    :param output: Path to output file.
    """
    with rasterio.open(band) as b:
        source = b.read().astype(np.float32)

    # If the source is a numpy array, reshape it to image if it has 3+ bands.
    source = np.ma.squeeze(source)
    if len(source.shape) >= 3:
        arr = reshape_as_image(source)
    else:
        arr = source
    if arr.ndim >= 3:
        # Adjust each band by the min/max so it will plot as RGB.
        arr = reshape_as_raster(arr)
        for ii, band in enumerate(arr):
            arr[ii] = adjust_band(band, kind="linear")
        arr = reshape_as_image(arr)

    save_as_img(raster=arr, output=output, cmap=color_map)


def apply_mask(
    filename: Path,
    geojson: Path,
    geojson_crs: str = "epsg:4326",
    output: Path | None = None,
    override_no_data: float | None = None,
) -> Path:
    """
    Crop image data (jp2 imagery file) by shape.

    :param filename: Path to input file.
    :param geojson: Geometry in GeoJSON format.
    :param geojson_crs: Coordinate reference system of the GeoJSON file. If different from the input file, the shape will be projected.
    :param output: Path to output file. If not provided, the output will be saved in the same directory as the input file.
    :param override_no_data: Value to fill outside the crop area. Useful to separate no data of fill. Raises `ValueError` if this value is present in the raster.
    :return: Path to output file.
    """
    if not output:
        output = filename.parent / f"{filename.stem}_masked.tif"

    if not output.parent.exists():
        output.parent.mkdir(parents=True)

    with rasterio.open(filename) as file:
        dsc = file.crs

    geojson = read_geojson(geojson)
    if geojson_crs != dsc:
        shp = project_shape(geojson["features"][0]["geometry"])
    else:
        shp = geojson["features"][0]["geometry"]

    crop_by_shape(filename=filename, output=str(output), geom=shp, override_no_data=override_no_data)

    return output


def rescale_band(band: np.ndarray, kwargs: dict) -> Tuple[np.ndarray, dict]:
    """
    Rescale band image data to 10 meters per pixel resolution.

    :param band: Band image array data.
    :param kwargs: Band image metadata.
    :return: Rescaled band image array data and metadata.
    """
    img_resolution = kwargs["transform"][0]
    scale_factor = img_resolution / 10

    # Scale the image to a resolution of 10m per pixel
    if img_resolution != 10:
        new_kwargs = kwargs.copy()
        new_kwargs["height"] = int(kwargs["height"] * scale_factor)
        new_kwargs["width"] = int(kwargs["width"] * scale_factor)
        new_kwargs["transform"] = rasterio.Affine(
            10, kwargs["transform"][1], kwargs["transform"][2], kwargs["transform"][3], -10, kwargs["transform"][5]
        )

        rescaled_raster = np.ndarray(
            shape=(kwargs["count"], new_kwargs["height"], new_kwargs["width"]), dtype=np.float32
        )

        reproject(
            source=band,
            destination=rescaled_raster,
            src_transform=kwargs["transform"],
            src_crs=kwargs["crs"],
            dst_resolution=(new_kwargs["width"], new_kwargs["height"]),
            dst_transform=new_kwargs["transform"],
            dst_crs=new_kwargs["crs"],
            resampling=Resampling.nearest,
        )
        band = rescaled_raster
        kwargs = new_kwargs

    return band, kwargs
