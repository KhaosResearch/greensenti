import zipfile
from datetime import datetime
from pathlib import Path

from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt, read_geojson


def download(
    dhus_username: str,
    dhus_password: str,
    dhus_host: str,
    geojson: Path,
    from_date: datetime,
    to_date: datetime,
    skip_unzip: bool = False,
    *,
    output: Path = Path("."),
):
    """
    Downloads products from D-HUS.

    :param geojson: GeoJSON file with product geometries.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param output: Output folder.
    :param skip_unzip: Whether to skip product unzip.
    :return:
    """
    # Load geojson file* and download products for an interval of dates.
    #  *see: http://geojson.io/
    geojson = read_geojson(geojson)
    footprint = geojson_to_wkt(geojson)

    sentinel_api = SentinelAPI(dhus_username, dhus_password, dhus_host, show_progressbars=False)

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

    print(f"Found {len(ids)} scenes between {from_date} and {to_date}")

    # Download products.
    product_infos, triggered, failed_downloads = sentinel_api.download_all(
        ids, str(output), max_attempts=10, n_concurrent_dl=1, lta_retry_delay=600
    )

    print(f"Success: {len(product_infos)}")
    print(f"Triggered: {len(triggered)}")
    print(f"Failed: {len(failed_downloads)}")

    if not skip_unzip:
        for product_id, product_info in product_infos.items():
            title = product_info["title"]

            print(f"Unzipping {title}")

            # Make sure the output folder exists.
            data_dir = Path(output, title)
            data_dir.mkdir(parents=True, exist_ok=True)

            zip_filename = Path(output, title + ".zip")

            if Path(data_dir, title).is_dir():
                continue

            with zipfile.ZipFile(zip_filename, "r") as zip_file:
                zip_file.extractall(data_dir)

    return product_infos, triggered, failed_downloads
