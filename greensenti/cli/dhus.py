import zipfile
from datetime import datetime
from pathlib import Path

import typer
from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt, read_geojson

from greensenti.settings import BaseSettings

app = typer.Typer()
settings = BaseSettings()


@app.command()
def download(
    geojson: Path = typer.Argument(..., exists=True, file_okay=True, help="GeoJSON"),
    from_date: datetime = typer.Argument(..., formats=["%Y-%m-%d"], help="From date (begin date)"),
    to_date: datetime = typer.Argument(..., formats=["%Y-%m-%d"], help="To date (end date)"),
    output: Path = typer.Option(Path("."), help="Output folder"),
    skip_unzip: bool = typer.Option(False, help="Skip product unzip."),
):
    """
    Downloads products from DHUS.

    :param geojson: GeoJSON file with product geometries.
    :param from_date: From date (begin date).
    :param to_date: To date (end date).
    :param output: Output folder.
    :param skip_unzip: Skip product unzip.
    :return:
    """
    # Load geojson file* and download products for an interval of dates.
    #  *see: http://geojson.io/
    geojson = read_geojson(geojson)
    footprint = geojson_to_wkt(geojson)

    sentinel_api = SentinelAPI(
        settings.dhus_username, settings.dhus_password, settings.dhus_host, show_progressbars=False
    )

    typer.echo("Searching for products in scene")

    # Search is limited to those scenes that intersect with the AOI
    # (area of interest) polygon.
    products = sentinel_api.query(
        area=footprint,
        filename="S2*",
        producttype="S2MSI2A",
        platformname="Sentinel-2",
        cloudcoverpercentage=(0, 100),
        date=(from_date, to_date),
    )

    # Get the list of products.
    products_df = sentinel_api.to_dataframe(products)
    ids = products_df.index

    typer.echo(f"Found {len(ids)} scenes between {from_date} and {to_date}")

    # Download products.
    product_infos, triggered, failed_downloads = sentinel_api.download_all(
        ids, output, max_attempts=10, n_concurrent_dl=1, lta_retry_delay=600
    )

    typer.echo(f"Success: {len(product_infos)}")
    typer.echo(f"Triggered: {len(triggered)}")
    typer.echo(f"Failed: {len(failed_downloads)}")

    if not skip_unzip:
        for product_id, product_info in product_infos.items():
            title = product_info["title"]

            typer.echo(f"Unzipping {title}")

            # Make sure the output folder exists.
            data_dir = Path(output, title)
            data_dir.mkdir(parents=True, exist_ok=True)

            zip_filename = Path(output, title + ".zip")

            if Path(data_dir, title).is_dir():
                typer.echo(f"{title} already unzipped")
                continue

            with zipfile.ZipFile(zip_filename, "r") as zip_file:
                zip_file.extractall(data_dir)

    return product_infos, triggered, failed_downloads
