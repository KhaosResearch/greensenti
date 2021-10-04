from pathlib import Path

import numpy as np
import pyproj
import rasterio
import typer
from matplotlib import pyplot as plt
from rasterio import mask
from rasterio.plot import adjust_band, reshape_as_image, reshape_as_raster
from sentinelsat import read_geojson
from shapely.geometry import shape
from shapely.ops import transform

app = typer.Typer()


def crop_by_shape(filename: str, geom, outfile: str) -> None:
    """
    Crop input file with a polygon mask.

    :param filename: Input image.
    :param geom: Geometry.
    :param outfile: Path to output file.
    """
    # Load the raster, mask it by the polygon and crop it.
    with rasterio.open(filename) as src:
        out_image, out_transform = mask.mask(src, shapes=[geom], crop=True)
    out_meta = src.meta.copy()

    # Save the resulting raster.
    out_meta.update(
        {"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform}
    )
    with rasterio.open(outfile, "w", **out_meta) as dest:
        dest.write(out_image)


def project_shape(geom, scs="epsg:4326", dcs="epsg:32630"):
    """
    Project a shape from a source coordinate system to another one.
    The source coordinate system can be obtain with `rasterio` as illustrated next:

    >>> import rasterio
    >>> print(rasterio.open('example.jp2').crs)

    This is useful when the geometry has its points in "normal" coordinate reference systems while the geoTiff/jp2 data
    is expressed in other coordinate system.

    :param geom: Geometry, e.g., [{'type': 'Polygon', 'coordinates': [[(1,2), (3,4), (5,6), (7,8), (9,10)]]}]
    :param scs: Source reference coordinate system.
    :param dcs: Destination reference coordinate system.
    :return: Geometry in destination coordinate system.
    """
    init_crs = pyproj.CRS(scs)
    final_crs = pyproj.CRS(dcs)

    project = pyproj.Transformer.from_crs(init_crs, final_crs, always_xy=True).transform

    return transform(project, shape(geom))


def save_as_img(raster: np.array, output: str, **kwargs) -> str:
    """
    Save raster image to file.
    """
    fig, ax = plt.subplots(figsize=plt.figaspect(raster), frameon=False)
    fig.subplots_adjust(0, 0, 1, 1)

    ax.imshow(raster, **kwargs)

    # Export to file.
    fig.savefig(output, dpi=300, transparent=True)

    # Close figure to avoid overflow.
    plt.close(fig)

    return output


@app.command()
def transform_image(
    band: Path = typer.Argument(..., exists=True, file_okay=True, help="TIF image"),
    output: Path = typer.Option(..., file_okay=True, help="Output file"),
    color_map: str = typer.Option(None, "--cmap", help="Color map"),
) -> Path:
    """
    Transform raster to image (see full list of accepted drivers at https://gdal.org/drivers/raster/index.html).
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

    save_as_img(raster=arr, output=str(output), cmap=color_map)

    return output


@app.command()
def apply_mask(
    filename: Path = typer.Argument(..., exists=True, file_okay=True, help="Path to input file"),
    geojson: Path = typer.Argument(..., file_okay=True),
    output: Path = typer.Option(..., help="Path to output file"),
) -> Path:
    """
    Crop image data (jp2 imagery file) by shape.

    :return: Path to output file.
    """
    # Make sure the output dir exists.
    if not output.parent.is_dir():
        output.parent.mkdir(parents=True)

    # Load geojson file*
    # *see: http://geojson.io/
    geojson = read_geojson(geojson)
    shape = project_shape(geojson["features"][0]["geometry"])

    # Mask product based on location.
    crop_by_shape(filename=str(filename), outfile=str(output), geom=shape)

    return output
