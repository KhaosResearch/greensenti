from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
import typer

# allow division by zero
np.seterr(divide="ignore", invalid="ignore")

app = typer.Typer()


@app.command()
def cloud_cover_percentage(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band (20m)"),
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band (20m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="B11 band (20m)"),
    tau: float = typer.Option(0.2, help="tau parameter"),
) -> float:
    """
    Computes cloud percentage of an image based on:

    * https://github.com/sentinel-hub/custom-scripts/tree/master/sentinel-2/cby_cloud_detection#

    :param b3: B03 band (20m).
    :param b4: B04 band (20m).
    :param b11: B11 band (20m).
    :param tau: tau coefficient for the cloud detection algorithm.
    :return: Cloud cover percentage.
    """
    with rasterio.open(b3) as green:
        GREEN = green.read(1).astype(np.float32)
    with rasterio.open(b4) as red:
        RED = red.read(1).astype(np.float32)
    with rasterio.open(b11) as swir11:
        SWIR11 = swir11.read(1).astype(np.float32)

    # convert to surface reflectance
    GREEN = GREEN / 10000
    RED = RED / 10000
    SWIR11 = SWIR11 / 10000

    # detect which elements are cloud based on Braaten-Cohen-Yang cloud detector
    bRatio = (GREEN - 0.175) / (0.39 - 0.175)
    NGDR = (GREEN - RED) / (GREEN + RED)

    is_cloud = ((bRatio > 1) | ((bRatio > 0) & (NGDR > 0))) & (GREEN != 0) & (SWIR11 > tau)

    # compute and return cloud percentage
    cloud_cover_percentage = np.count_nonzero(is_cloud) * 100 / np.count_nonzero(GREEN)

    typer.echo(f"Cloud cover percentage: {cloud_cover_percentage}%")

    return cloud_cover_percentage


@app.command()
def true_color(
    r: Path = typer.Argument(..., exists=True, file_okay=True, help="RED band (B04 for Sentinel-2, 10m)"),
    g: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN band (B03 for Sentinel-2, 10m)"),
    b: Path = typer.Argument(..., exists=True, file_okay=True, help="BLUE band (B02 for Sentinel-2, 10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> None:
    """
    Computes true color image (RGB).

    :param r: RED band (B04 for Sentinel-2, 10m).
    :param g: GREEN band (B03 for Sentinel-2, 10m).
    :param b: BLUE band (B02 for Sentinel-2, 10m).
    :output: Path to output file.
    """
    with rasterio.open(r) as red:
        red_band = red.read(1).astype(np.float32)
        kwargs = red.meta
    with rasterio.open(g) as green:
        green_band = green.read(1).astype(np.float32)
    with rasterio.open(b) as blue:
        blue_band = blue.read(1).astype(np.float32)

    # create true color image
    # adjust each band by the min-max so it will plot as RGB
    rgb_image = np.dstack((red_band, green_band, blue_band))

    max_pixel_value = rgb_image.max()
    rgb_image = np.multiply(rgb_image, 255.0)
    rgb_image = np.divide(rgb_image, max_pixel_value)
    rgb_image = rgb_image.astype(np.uint8)

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=3)
        with rasterio.open(output, "w", **kwargs) as rgb:
            rgb.write(red_band.astype(rasterio.float32), 1)
            rgb.write(green_band.astype(rasterio.float32), 2)
            rgb.write(blue_band.astype(rasterio.float32), 3)

        typer.echo(f"exported to: {output.absolute()}")


@app.command()
def moisture(
    b8a: Path = typer.Argument(..., exists=True, file_okay=True, help="B8A band (60m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="B11 band (60m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute moisture index.

    :param b8a: B8A band (60m).
    :param b11: B11 band (60m).
    :output: Path to output file.
    :return: Moisture index.
    """
    with rasterio.open(b8a) as band:
        band_8a = band.read(1).astype(np.float32)
        kwargs = band.meta
    with rasterio.open(b11) as band:
        band_11 = band.read(1).astype(np.float32)

    # compute the index
    moisture = (band_8a - band_11) / (band_8a + band_11)
    value = np.nanmean(moisture)

    typer.echo(f"index value: {value}")

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(moisture.astype(rasterio.float32), 1)

        typer.echo(f"exported to: {output.absolute()}")

    return value


@app.command()
def ndvi(
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="RED band (B04 for Sentinel-2, 10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="NIR band (B08 for Sentinel-2, 10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Vegetation Index (NDVI).
    Value ranges from -1 to 1. Negative values correspond to water.
    Values close to zero (-0.1 to 0.1) generally correspond to barren areas of rock, sand, or snow. Low,
    positive values represent shrub and grassland (approximately 0.2 to 0.4), while high values indicate
    temperate and tropical rainforests (values approaching 1).

    ..note:: https://eos.com/index-stack/
    ..note:: https://medium.com/analytics-vidhya/satellite-imagery-analysis-with-python-3f8ccf8a7c32

    :param b4: RED band (B04 for Sentinel-2, 10m).
    :param b8: NIR band (B08 for Sentinel-2, 10m).
    :output: Path to output file.
    :return: NDVI index value.
    """
    with rasterio.open(b4) as red:
        RED = red.read(1).astype(np.float32)
        kwargs = red.meta
    with rasterio.open(b8) as nir:
        NIR = nir.read(1).astype(np.float32)

    # compute the index
    ndvi = (NIR - RED) / (NIR + RED)
    value = np.nanmean(ndvi)

    typer.echo(f"index value: {value}")

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndvi.astype(rasterio.float32), 1)

        typer.echo(f"exported to: {output.absolute()}")

    return value


@app.command()
def ndsi(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN band (B03 for Sentinel-2, 20m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="SWIR band (B11 for Sentinel-2, 20m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Snow Index (NDSI) index.
    Values above 0.42 are usually snow.

    ..note:: https://eos.com/index-stack/

    :param b3: GREEN band (B03 for Sentinel-2, 20m).
    :param b11: SWIR band (B11 for Sentinel-2, 20m).
    :output: Path to output file.
    :return: NDSI index value.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        kwargs = band.meta
    with rasterio.open(b11) as band:
        band_11 = band.read(1).astype(np.float32)

    # allow division by zero
    np.seterr(divide="ignore", invalid="ignore")

    # compute the index
    ndsi = (band_3 - band_11) / (band_3 + band_11)
    ndsi = (ndsi < 0.42) * 1  # apply threshold (values above 0.42 are regarded as snowy)
    value = np.nanmean(ndsi)

    typer.echo(f"index value: {value}")

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndsi.astype(rasterio.float32), 1)

        typer.echo(f"exported to: {output.absolute()}")

    return value


@app.command()
def ndwi(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN band (B03 for Sentinel-2)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="NIR band (B08 for Sentinel-2)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Water Index (NDWI) index.

    ..note:: https://eos.com/index-stack/

    :param b3: GREEN band (B03 for Sentinel-2).
    :param b8: NIR band (B08 for Sentinel-2).
    :output: Path to output file.
    :return: NDWI index value.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        kwargs = band.meta
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)

    # compute the index
    ndwi = (band_3 - band_8) / (band_3 + band_8)
    value = np.nanmean(ndwi)

    typer.echo(f"index value: {value}")

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndwi.astype(rasterio.float32), 1)

        typer.echo(f"exported to: {output.absolute()}")

    return value


@app.command()
def evi(
    b2: Path = typer.Argument(..., exists=True, file_okay=True, help="B02 band (10m)"),
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band (10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Enhanced Vegetation Index (EVI) index.
    Its value ranges from -1 to 1, with healthy vegetation generally around 0.20 to 0.80.

    :param b2: B02 band (10m).
    :param b4: B04 band (10m).
    :param b8: B04 band (10m).
    :output: Path to output file.
    :return: EVI index value.
    """
    with rasterio.open(b2) as band:
        band_2 = band.read(1).astype(np.float32)
        kwargs = band.meta
    with rasterio.open(b4) as band:
        band_4 = band.read(1).astype(np.float32)
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)

    # compute the index
    evi = (2.5 * (band_8 - band_4)) / (band_8 + 6 * band_4 - 7.5 * band_2 + 1)
    value = np.nanmean(evi)

    typer.echo(f"index value: {value}")

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(evi.astype(rasterio.float32), 1)

        typer.echo(f"exported to: {output.absolute()}")

    return value
