import zipfile
from datetime import datetime
from pathlib import Path

import typer
from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt, read_geojson

from greensenti.settings import settings


def dhus_download(
    geojson: Path = typer.Argument(..., exists=True, file_okay=True, help="GeoJSON"),
    from_date: datetime = typer.Argument(..., formats=["%Y-%m-%d"], help="From date (begin date)"),
    to_date: datetime = typer.Argument(..., formats=["%Y-%m-%d"], help="To date (end date)"),
    output: Path = typer.Option(Path("."), help="Output folder"),
    skip_unzip: bool = typer.Option(False, help="Skip product unzip."),
):
    """
    Downloads products from DHUS.
    """
    # load geojson file* and download products for an interval of dates
    #  *see: http://geojson.io/
    geojson = read_geojson(geojson)
    footprint = geojson_to_wkt(geojson)

    # initialize Sentinel client
    sentinel_api = SentinelAPI(
        settings.DHUS_USERNAME, settings.DHUS_PASSWORD, settings.DHUS_HOST, show_progressbars=False
    )

    typer.echo("searching products in scene")

    # search is limited to those scenes that intersect with the AOI (area of interest) polygon
    products = sentinel_api.query(
        area=footprint,
        filename="S2*",
        producttype="S2MSI2A",
        platformname="Sentinel-2",
        cloudcoverpercentage=(0, 100),
        date=(from_date, to_date),
    )

    products_df = sentinel_api.to_dataframe(products)
    uid_products = products_df.index
    num_products = len(uid_products)

    typer.echo(f"found {num_products} scenes between {from_date} and {to_date}")

    with typer.progressbar(uid_products, label="Processing products") as progress:
        for product in progress:
            p = products_df.loc[[product]]
            p_title = p["title"].values[0]
            p_uuid = p["uuid"].values[0]

            typer.echo(f"processing {p_title}")

            data_dir = Path(output, p_title)
            data_dir.mkdir(parents=True, exist_ok=True)

            # download zip-compressed scene to file system
            zip_filename = Path(data_dir, p_title + ".zip")
            if not zip_filename.is_file():
                sentinel_api.download(p_uuid, directory_path=data_dir)

            if not skip_unzip:
                # unzip file
                typer.echo(f"unzip {p_title}")

                safe_dir = Path(data_dir, p_title + ".SAFE")
                if not safe_dir.is_dir():
                    with zipfile.ZipFile(zip_filename, "r") as zip_file:
                        zip_file.extractall(data_dir)

    typer.echo(f"processed {num_products} products")
