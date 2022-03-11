from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
import typer
from rasterio.warp import reproject, Resampling

# Allow division by zero.
np.seterr(divide="ignore", invalid="ignore")

app = typer.Typer()


@app.command()
def cloud_cover_percentage(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band for Sentinel-2 (20m)"),
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band for Sentinel-2 (20m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="B11 band for Sentinel-2 (20m)"),
    tau: float = typer.Option(0.2, help="tau parameter"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> float:
    """
    Computes cloud percentage of an image based on:

    * https://github.com/sentinel-hub/custom-scripts/tree/master/sentinel-2/cby_cloud_detection#

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    :param b3: B03 band (20m).
    :param b4: B04 band (20m).
    :param b11: B11 band (20m).
    :param tau: `tau` coefficient for the cloud detection algorithm.
    :param output: Path to output file.
    :return: Cloud cover mask.
    """
    with rasterio.open(b3) as green:
        GREEN = green.read(1).astype(np.float32)
        GREEN[GREEN == 0] = np.nan
        kwargs = green.meta
    with rasterio.open(b4) as red:
        RED = red.read(1).astype(np.float32)
        RED[RED == 0] = np.nan
    with rasterio.open(b11) as swir11:
        SWIR11 = swir11.read(1).astype(np.float32)
        SWIR11[SWIR11 == 0] = np.nan

    # Convert to surface reflectance.
    GREEN = GREEN / 10000
    RED = RED / 10000
    SWIR11 = SWIR11 / 10000

    # Detect which elements are cloud based on Braaten-Cohen-Yang cloud detector.
    bRatio = (GREEN - 0.175) / (0.39 - 0.175)
    NGDR = (GREEN - RED) / (GREEN + RED)

    is_cloud = ((bRatio > 1) | ((bRatio > 0) & (NGDR > 0))) & (GREEN != 0) & (SWIR11 > tau)

    # Compute and return cloud percentage.
    cloud_cover_percentage = np.count_nonzero(is_cloud) * 100 / np.count_nonzero(GREEN)

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(is_cloud.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return cloud_cover_percentage

@app.command()
def cloud_mask(
    scl: Path = typer.Argument(..., exists=True, file_okay=True, help="SCL band for Sentinel-2 (20m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Computes cloud mask of an image based on the SCL raster provided by sentinel.

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    :param scl: SCL band (20m).
    :param output: Path to output file.
    :return: Cloud cover mask.
    """ 
    scl_cloud_values = [3,8,9,10,11] # Classification band's cloud-related values
    with rasterio.open(scl, "r") as cloud_mask_file:
        kwargs = cloud_mask_file.meta
        cloud_mask = cloud_mask_file.read(1)

    # Calculate cloud mask from Sentinel's cloud related values
    cloud_mask = np.isin(cloud_mask,scl_cloud_values).astype(np.int8)

    dst_kwargs = kwargs.copy()
    dst_kwargs['driver'] = 'GTiff'
    # height and width is duplicated as input raster has 20m spatial resolution
    dst_kwargs["height"] = int(kwargs["height"] * 2) 
    dst_kwargs["width"] = int(kwargs["width"] * 2)
    dst_kwargs["transform"] = rasterio.Affine(10, 0.0, kwargs["transform"][2], 0.0, -10, kwargs["transform"][5])

    output_band = np.ndarray(shape=(dst_kwargs["height"],dst_kwargs["width"]), dtype=np.int8)
    reproject(
        source=cloud_mask,
        destination=output_band,
        src_transform=kwargs['transform'],
        src_crs=kwargs['crs'],
        dst_resolution=(dst_kwargs['width'], dst_kwargs['height']),
        dst_transform=dst_kwargs['transform'],
        dst_crs=dst_kwargs['crs'],
        resampling=Resampling.nearest,
    )

    output_band = output_band.reshape((dst_kwargs['count'],*output_band.shape))
    if output:
        with rasterio.open(output, "w", **dst_kwargs) as output_:
            output_.write(output_band)

        print(f"exported to: {output.absolute()}")

    return output_band    

@app.command()
def true_color(
    r: Path = typer.Argument(..., exists=True, file_okay=True, help="RED - B04 band for Sentinel-2 (10m)"),
    g: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN - B03 band for Sentinel-2 (10m)"),
    b: Path = typer.Argument(..., exists=True, file_okay=True, help="BLUE - B02 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Computes true color image composite (RGB).

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    :param r: RED band (B04 for Sentinel-2, 10m).
    :param g: GREEN band (B03 for Sentinel-2, 10m).
    :param b: BLUE band (B02 for Sentinel-2, 10m).
    :return: True color image.
    """
    with rasterio.open(r) as red:
        red_band = red.read(1).astype(np.float32)
        kwargs = red.meta
    with rasterio.open(g) as green:
        green_band = green.read(1).astype(np.float32)
    with rasterio.open(b) as blue:
        blue_band = blue.read(1).astype(np.float32)

    # Create true color image.
    # Adjust each band by the min-max so it will plot as RGB.
    rgb_image = np.dstack((red_band, green_band, blue_band))

    max_pixel_value = rgb_image.max()
    rgb_image = np.multiply(rgb_image, 255.0)
    rgb_image = np.divide(rgb_image, max_pixel_value)
    rgb_image = rgb_image.astype(np.uint8)

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=3)
        with rasterio.open(output, "w", **kwargs) as rgb:
            rgb.write(red_band.astype(rasterio.float32), 1)
            rgb.write(green_band.astype(rasterio.float32), 2)
            rgb.write(blue_band.astype(rasterio.float32), 3)
        typer.echo(output.absolute())

    return rgb_image


@app.command()
def moisture(
    b8a: Path = typer.Argument(..., exists=True, file_okay=True, help="B8A band for Sentinel-2 (60m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="B11 band for Sentinel-2 (60m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute moisture index.

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    :param b8a: B8A band (60m).
    :param b11: B11 band (60m).
    :param output: Path to output file.
    :return: Moisture index.
    """
    with rasterio.open(b8a) as band:
        band_8a = band.read(1).astype(np.float32)
        band_8a[band_8a == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b11) as band:
        band_11 = band.read(1).astype(np.float32)
        band_11[band_11 == 0] = np.nan

    moisture = (band_8a - band_11) / (band_8a + band_11)

    moisture[moisture == np.inf] = np.nan
    moisture[moisture == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(moisture.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return moisture


@app.command()
def ndvi(
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="RED - B04 band for Sentinel-2 (10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="NIR - B08 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Vegetation Index (NDVI).
    Value ranges from -1 to 1. Negative values correspond to water.
    Values close to zero (-0.1 to 0.1) generally correspond to barren areas of rock, sand, or snow. Low,
    positive values represent shrub and grassland (approximately 0.2 to 0.4), while high values indicate
    temperate and tropical rainforests (values approaching 1).

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    ..note:: https://eos.com/index-stack/

    ..note:: https://medium.com/analytics-vidhya/satellite-imagery-analysis-with-python-3f8ccf8a7c32

    :param b4: RED - B04 band for Sentinel-2 (10m).
    :param b8: NIR - B08 band for Sentinel-2 (10m).
    :param output: Path to output file.
    :return: NDVI index.
    """
    with rasterio.open(b4) as red:
        RED = red.read(1).astype(np.float32)
        RED[RED == 0] = np.nan
        kwargs = red.meta
    with rasterio.open(b8) as nir:
        NIR = nir.read(1).astype(np.float32)
        NIR[NIR == 0] = np.nan

    ndvi = (NIR - RED) / (NIR + RED)

    ndvi[ndvi == np.inf] = np.nan
    ndvi[ndvi == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, nodata=np.nan, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndvi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ndvi


@app.command()
def ndsi(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN - B03 band for Sentinel-2 (20m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="SWIR - B11 band for Sentinel-2 (20m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Snow Index (NDSI) index.
    Values above 0.42 are usually snow.

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    ..note:: https://eos.com/index-stack/

    :param b3: GREEN band (B03 for Sentinel-2, 20m).
    :param b11: SWIR band (B11 for Sentinel-2, 20m).
    :param output: Path to output file.
    :return: NDSI index.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b11) as band:
        band_11 = band.read(1).astype(np.float32)
        band_11[band_11 == 0] = np.nan

    ndsi = (band_3 - band_11) / (band_3 + band_11)
    ndsi = (ndsi > 0.42) * 1.0  # TODO apply threshold (values above 0.42 are regarded as snowy)

    ndsi[ndsi == np.inf] = np.nan
    ndsi[ndsi == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndsi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ndsi


@app.command()
def ndwi(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="GREEN - B03 band for Sentinel-2 (10m))"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="NIR - B08 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Water Index (NDWI) index.

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    ..note:: https://eos.com/index-stack/

    :param b3: GREEN band (B03 for Sentinel-2).
    :param b8: NIR band (B08 for Sentinel-2).
    :param output: Path to output file.
    :return: NDWI index.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)
        band_8[band_8 == 0] = np.nan

    ndwi = (band_3 - band_8) / (band_3 + band_8)

    ndwi[ndwi == np.inf] = np.nan
    ndwi[ndwi == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndwi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ndwi


@app.command()
def evi2(
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band (10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="B08 band (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Enhanced Vegetation Index 2 (EVI2) index.

    :param b4: B04 band (10m).
    :param b8: B08 band (10m).
    :param output: Path to output file.
    :return: EVI2 index.
    """
    with rasterio.open(b4) as band:
        band_4 = band.read(1).astype(np.float32)
        band_4[band_4 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)
        band_8[band_8 == 0] = np.nan

    evi2 = 2.4 * ((band_8 - band_4) / (band_8 + band_4 + 1.0))

    evi2[evi2 == np.inf] = np.nan
    evi2[evi2 == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(evi2.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return evi2


@app.command()
def osavi(
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band (10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="B08 band (10m)"),
    Y: float = typer.Option(0.16, help="Y parameter"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Optimized Soil Adjusted Vegetation Index (OSAVI) index.

    :param b4: B04 band (10m).
    :param b8: B08 band (10m).
    :param Y: Y coefficient.
    :param output: Path to output file.
    :return: OSAVI index.
    """
    with rasterio.open(b4) as band:
        band_4 = band.read(1).astype(np.float32)
        band_4[band_4 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)
        band_8[band_8 == 0] = np.nan

    osavi = (1 + Y) * (band_8 - band_4) / (band_8 + band_4 + Y)

    osavi[osavi == np.inf] = np.nan
    osavi[osavi == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(osavi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return osavi


@app.command()
def ndre(
    b5: Path = typer.Argument(..., exists=True, file_okay=True, help="B05 band (60m)"),
    b9: Path = typer.Argument(..., exists=True, file_okay=True, help="B09 band (60m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Normalized Difference NIR/Rededge Normalized Difference Red-Edge (NDRE) index.

    :param b5: B05 band (60m).
    :param b9: B09 band (60m).
    :param output: Path to output file.
    :return: NDRE index.
    """
    with rasterio.open(b5) as band:
        band_5 = band.read(1).astype(np.float32)
        band_5[band_5 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b9) as band:
        band_9 = band.read(1).astype(np.float32)
        band_9[band_9 == 0] = np.nan

    ndre = (band_9 - band_5) / (band_9 + band_5)

    ndre[ndre == np.inf] = np.nan
    ndre[ndre == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndre.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ndre


@app.command()
def mndwi(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band (20m)"),
    b11: Path = typer.Argument(..., exists=True, file_okay=True, help="B11 band (20m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Modified NDWI (MNDWI) index.

    :param b3: B03 band (20m).
    :param b11: B11 band (20m).
    :param output: Path to output file.
    :return: MNDWI index.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b11) as band:
        band_11 = band.read(1).astype(np.float32)
        band_11[band_11 == 0] = np.nan

    mndwi = (band_3 - band_11) / (band_3 + band_11)

    mndwi[mndwi == np.inf] = np.nan
    mndwi[mndwi == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(mndwi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return mndwi


@app.command()
def bri(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band (10m)"),
    b5: Path = typer.Argument(..., exists=True, file_okay=True, help="B05 band (20m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="B08 band (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Browning Reflectance Index (BRI) index.

    :param b3: B03 band (10m).
    :param b5: B05 band (20m).
    :param b8: B08 band (10m).
    :param output: Path to output file.
    :return: BRI index.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b5) as band:
        band_5_20m = band.read(1).astype(np.float32)
        band_5 = np.repeat(np.repeat(band_5_20m, 2, axis=0), 2, axis=1)
        band_5[band_5 == 0] = np.nan
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)
        band_8[band_8 == 0] = np.nan

    bri = (1 / band_3 - 1 / band_5) / band_8

    bri[bri == np.inf] = np.nan
    bri[bri == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(bri.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return bri


@app.command()
def evi(
    b2: Path = typer.Argument(..., exists=True, file_okay=True, help="B02 band for Sentinel-2 (10m)"),
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band for Sentinel-2 (10m)"),
    b8: Path = typer.Argument(..., exists=True, file_okay=True, help="B08 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Enhanced Vegetation Index (EVI) index.
    Its value ranges from -1 to 1, with healthy vegetation generally around 0.20 to 0.80.

    ..note:: In Sentinel-2 Level-2A products, zero values are reserved for 'No Data'.
     This value is used to define which pixels should be masked. See also:

    * https://docs.digitalearthafrica.org/en/latest/data_specs/Sentinel-2_Level-2A_specs.html

    :param b2: B02 band (10m).
    :param b4: B04 band (10m).
    :param b8: B08 band (10m).
    :param output: Path to output file.
    :return: EVI index.
    """
    with rasterio.open(b2) as band:
        band_2 = band.read(1).astype(np.float32)
        band_2[band_2 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b4) as band:
        band_4 = band.read(1).astype(np.float32)
        band_4[band_4 == 0] = np.nan
    with rasterio.open(b8) as band:
        band_8 = band.read(1).astype(np.float32)
        band_8[band_8 == 0] = np.nan

    evi = (2.5 * (band_8 - band_4)) / ((band_8 + 6 * band_4 - 7.5 * band_2) + 1)

    evi[evi == np.inf] = np.nan
    evi[evi == -np.inf] = np.nan

    if output:
        # update kwargs to reflect change in data type
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(evi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return evi


@app.command()
def ndyi(
    b2: Path = typer.Argument(..., exists=True, file_okay=True, help="B02 band for Sentinel-2 (10m)"),
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Yellow Index (NDYI) index.

    * https://doi.org/10.1016/j.rse.2020.111660

    :param b2: B02 for Sentinel-2.
    :param b3: B03 for Sentinel-2.
    :param output: Path to output file.
    :return: NDYI index.
    """
    with rasterio.open(b2) as band:
        band_2 = band.read(1).astype(np.float32)
        band_2[band_2 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan

    ndyi = (band_3 - band_2) / (band_3 + band_2)

    ndyi[ndyi == np.inf] = np.nan
    ndyi[ndyi == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ndyi.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ndyi


@app.command()
def ri(
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band for Sentinel-2 (10m))"),
    b4: Path = typer.Argument(..., exists=True, file_okay=True, help="B04 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Normalized Difference Red/Green Redness (RI) index.

    :param b3: B03 for Sentinel-2.
    :param b4: B04 for Sentinel-2.
    :param output: Path to output file.
    :return: RI index.
    """
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b4) as band:
        band_4 = band.read(1).astype(np.float32)
        band_4[band_4 == 0] = np.nan

    ri = (band_4 - band_3) / (band_4 + band_3)

    ri[ri == np.inf] = np.nan
    ri[ri == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(ri.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return ri


@app.command()
def cri1(
    b2: Path = typer.Argument(..., exists=True, file_okay=True, help="B02 band for Sentinel-2 (10m))"),
    b3: Path = typer.Argument(..., exists=True, file_okay=True, help="B03 band for Sentinel-2 (10m)"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
) -> np.array:
    """
    Compute Carotenoid Reflectance (CRI1) index.

    :param b2: B02 for Sentinel-2.
    :param b3: B03 for Sentinel-2.
    :param output: Path to output file.
    :return: CRI1 index.
    """
    with rasterio.open(b2) as band:
        band_2 = band.read(1).astype(np.float32)
        band_2[band_2 == 0] = np.nan
        kwargs = band.meta
    with rasterio.open(b3) as band:
        band_3 = band.read(1).astype(np.float32)
        band_3[band_3 == 0] = np.nan

    cri1 = (1 / band_2) / (1 / band_3)

    cri1[cri1 == np.inf] = np.nan
    cri1[cri1 == -np.inf] = np.nan

    if output:
        # Update kwargs to reflect change in data type.
        kwargs.update(driver="GTiff", dtype=rasterio.float32, count=1)
        with rasterio.open(output, "w", **kwargs) as gtif:
            gtif.write(cri1.astype(rasterio.float32), 1)
        typer.echo(output.absolute())

    return cri1
