import pyproj
import rasterio
from rasterio import mask
from shapely.geometry import shape
from shapely.ops import transform


def crop_by_shape(filename: str, geom, outfile: str) -> None:
    """
    Crop input file with a polygon mask.

    :param filename: Input image.
    :param geom: Geometry.
    :param outfile: Path to output file.
    """
    # load the raster, mask it by the polygon and crop it
    with rasterio.open(filename) as src:
        out_image, out_transform = mask.mask(src, shapes=[geom], crop=True)
    out_meta = src.meta.copy()

    # save the resulting raster
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
