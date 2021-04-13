from pathlib import Path

import numpy as np
import rasterio
import typer
from matplotlib import pyplot as plt
from rasterio.plot import adjust_band, reshape_as_image, reshape_as_raster
from sentinelsat import read_geojson

from greensenti.helpers import crop_by_shape, project_shape

app = typer.Typer()


def save_as_img(raster: np.array, output: str, **kwargs) -> str:
    """
    Save raster image to file.
    """
    # plot image
    fig, ax = plt.subplots(figsize=plt.figaspect(raster), frameon=False)
    fig.subplots_adjust(0, 0, 1, 1)

    ax.imshow(raster, **kwargs)

    # export to file
    fig.savefig(output, dpi=300, transparent=True)

    # close figure to avoid overflow
    plt.close(fig)

    return output


@app.command()
def transform_image(
    band: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band (20m)"),
    output: Path = typer.Option(..., file_okay=True, help="Output file"),
    color_map: str = typer.Option(None, "--cmap", help="Color map"),
) -> Path:
    """
    Transform raster to image (see full list of accepted drivers at https://gdal.org/drivers/raster/index.html).
    """
    with rasterio.open(band) as b:
        source = b.read().astype(np.float32)

    # the source is a numpy array reshape it to image if it has 3+ bands
    source = np.ma.squeeze(source)
    if len(source.shape) >= 3:
        arr = reshape_as_image(source)
    else:
        arr = source
    if arr.ndim >= 3:
        # adjust each band by the min/max so it will plot as RGB.
        arr = reshape_as_raster(arr)
        for ii, band in enumerate(arr):
            arr[ii] = adjust_band(band, kind="linear")
        arr = reshape_as_image(arr)

    save_as_img(raster=arr, output=str(output), cmap=color_map)

    return output


@app.command()
def apply_mask(
    filename: Path = typer.Argument(..., exists=True, file_okay=True, help="Input filename"),
    geojson: Path = typer.Argument(..., file_okay=True),
    output: Path = typer.Option(..., help="Output file"),
) -> Path:
    """
    Crop image data (jp2 imagery file) by shape.
    """
    # load geojson file*
    #  *see: http://geojson.io/
    geojson = read_geojson(geojson)
    shape = project_shape(geojson["features"][0]["geometry"])

    # mask product based on location
    crop_by_shape(filename=str(filename), outfile=str(output), geom=shape)

    return output
