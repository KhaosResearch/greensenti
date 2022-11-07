import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Union

import pandas as pd
from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt, read_geojson

try:
    GCLOUD_DISABLED = False
    from google.cloud import storage
except:
    GCLOUD_DISABLED = True


def download_by_text(
    text_match: str,
    from_date: Union[str, datetime] = None,
    to_date: Union[str, datetime] = None,
    *,
    unzip: bool = False,
    max_clouds: int = 100,
    output: Path = Path("."),
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> pd.DataFrame:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud by a text match with the product title.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param text_match: Regular expresion to match the product filename.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param unzip: Whether to skip product unzip.
    :param output: Output folder.
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: pandas dataframe with the product metadata and download status
    """
    return download(
        geojson=None,
        text_match=text_match,
        from_date=from_date,
        to_date=to_date,
        unzip=unzip,
        max_clouds=max_clouds,
        output=output,
        dhus_username=dhus_username,
        dhus_password=dhus_password,
        dhus_host=dhus_host,
        gcloud=gcloud,
    )


def download_by_geometry(
    geojson: Path,
    from_date: Union[str, datetime] = None,
    to_date: Union[str, datetime] = None,
    *,
    unzip: bool = False,
    max_clouds: int = 100,
    output: Path = Path("."),
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> pd.DataFrame:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud by a given geometry in GeoJSON format.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param geojson: GeoJSON file with product geometries.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param unzip: Whether to skip product unzip.
    :param output: Output folder.
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: pandas dataframe with the product metadata and download status
    """
    return download(
        geojson=geojson,
        text_match=None,
        from_date=from_date,
        to_date=to_date,
        unzip=unzip,
        max_clouds=max_clouds,
        output=output,
        dhus_username=dhus_username,
        dhus_password=dhus_password,
        dhus_host=dhus_host,
        gcloud=gcloud,
    )


def download(
    geojson: Path = None,
    text_match: str = "*",
    from_date: Union[str, datetime] = None,
    to_date: Union[str, datetime] = None,
    *,
    unzip: bool = False,
    max_clouds: int = 100,
    output: Path = Path("."),
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> pd.DataFrame:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param geojson: GeoJSON file with product geometries.
    :param text_match: Regular expresion to match the product filename.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param unzip: Whether to skip product unzip.
    :param output: Output folder.
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: pandas dataframe with the product metadata and download status
    """
    # Only use Google Cloud as backend is credentials are passed
    # and the optional dependency is installed
    if gcloud and GCLOUD_DISABLED:
        print(
            "Error: Missing required Google Cloud dependencies to download from GCloud, use `pip install greensenti[gcloud]` to install them."
        )
        exit(1)

    # Make sure dates are datetime, and if not set add sensible defaults
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    elif not from_date:
        from_date = datetime(1970, 1, 1)

    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
    elif not to_date:
        to_date = datetime.now()

    # Load geojson file* and download products for an interval of dates.
    #  *see: http://geojson.io/
    if geojson:
        geojson = read_geojson(geojson)
        footprint = geojson_to_wkt(geojson)
    else:
        footprint = None

    # Text match uses filename, to avoid users having to add unknown extensions,
    # add wildcard at the end
    if text_match:
        if not text_match.endswith("*"):
            text_match += "*"

    sentinel_api = SentinelAPI(dhus_username, dhus_password, dhus_host, show_progressbars=False)

    print("Searching for products in scene")

    # Search is limited to those scenes that intersect with the AOI
    # (area of interest) polygon.
    products = sentinel_api.query(
        area=footprint,
        filename=text_match,
        producttype="S2MSI2A",
        platformname="Sentinel-2",
        cloudcoverpercentage=(0, max_clouds),
        date=(from_date, to_date),
    )

    # Get the list of products.
    products_df = sentinel_api.to_dataframe(products)
    ids = products_df.index

    print(f"Found {len(ids)} scenes between {from_date} and {to_date}")

    if not gcloud:
        status_df = copernicous_download(ids, sentinel_api, output=output)
        products_df = pd.merge(products_df, status_df, how="outer", on="uuid")
    else:
        gcloud_api = gcloud_bucket()
        # Google cloud doesn't utilize ids, only titles
        titles = products_df["title"]
        status_df = gcloud_download(titles, gcloud_api, output=output)
        products_df = pd.merge(products_df, status_df, how="outer", on="title")

    print(f"Status: {status_df}")

    if unzip:
        for product in products_df.iterrows():
            title = product["title"]

            print(f"Unzipping {title}")

            # Make sure the output folder exists.
            data_dir = Path(output, title)
            data_dir.mkdir(parents=True, exist_ok=True)

            zip_filename = Path(output, title + ".zip")

            if Path(data_dir, title).is_dir():
                continue

            with zipfile.ZipFile(zip_filename, "r") as zip_file:
                zip_file.extractall(data_dir)

    return products_df


def copernicous_download(ids: List[str], api: SentinelAPI, output: Path = Path(".")) -> pd.DataFrame:
    """
    Downloads a list of Sentinel-2 products by a list of titles from Google Cloud.

    :param titles: Sentinel-2 product ids.
    :param api: Sentinelsat API object.
    :param output: Output folder.
    :return: pandas dataframe with the product status by id
    """
    product_info, triggered, failed_downloads = api.download_all(
        ids, str(output), max_attempts=10, n_concurrent_dl=1, lta_retry_delay=600
    )

    status = []

    for product in product_info:
        status.append(
            {
                "uuid": product,
                "status": "ok",
            }
        )

    for product in triggered:
        status.append(
            {
                "uuid": product,
                "status": "triggered",
            }
        )

    for product in failed_downloads:
        status.append(
            {
                "uuid": product,
                "status": "failed",
            }
        )

    return pd.DataFrame(status)


def gcloud_bucket() -> "storage.Bucket":
    """
    Connects to Google Cloud gcp-public-data-sentinel-2 bucket to download
    Sentinel-2 data.

    **Expects** the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :return: Google Cloud bucket object
    """
    client = storage.Client()
    return client.bucket("gcp-public-data-sentinel-2")


def gcloud_download(titles: str, api: "storage.Bucket", output: Path = Path(".")) -> pd.DataFrame:
    """
    Downloads a list of Sentinel-2 products by a list of titles from Google Cloud.

    :param titles: Sentinel-2 product titles.
    :param api: Google Cloud bucket object.
    :param output: Output folder.
    :return: pandas dataframe with the product status by title
    """
    status = []

    for title in titles:
        try:
            gcloud_path = get_gcloud_path(title)
            product_folder = os.path.basename(gcloud_path)

            blobs = api.list_blobs(prefix=gcloud_path)

            for blob in blobs:
                if blob.name.endswith("/") or blob.name.endswith("$folder$"):  # Ignore folders and GCloud files
                    continue

                # make sure temporal folder exists
                local_blob_dir = os.path.dirname(blob.name.removeprefix(gcloud_path + "/"))
                dir_ = os.path.join(output, product_folder, local_blob_dir)
                Path(dir_).mkdir(parents=True, exist_ok=True)

                # Remove fluff from blob name
                local_blob_name = os.path.basename(blob.name.removeprefix(gcloud_path))

                # Download to local file
                local_blob_path = os.path.join(dir_, local_blob_name)
                if not os.path.isfile(local_blob_path):
                    blob.download_to_filename(local_blob_path)
                else:
                    print("File exists, skipping")

            # Upload product zip file to minio
            local_product_folder = os.path.join(output, product_folder)
            local_zip_file = os.path.join(output, title)
            if not os.path.isfile(local_zip_file + ".zip"):
                shutil.make_archive(local_zip_file, "zip", local_product_folder)

            status.append(
                {
                    "title": title,
                    "status": "ok",
                }
            )
        except Exception as e:
            status.append(
                {
                    "title": title,
                    "status": "failed",
                }
            )

    return pd.DataFrame(status)


def get_gcloud_path(title: str) -> str:
    """
    Gets the google cloud bucket prefix for a given Sentinel-2 product.
    Products are group by tile id or MGRS coordinates.

    :param title: Sentinel-2 title.
    :return: Google Cloud path for title
    """
    tile_id = title.split("_T")[1]  # This is always a 2 digit and 3 letter ID  E.g: 30SUF
    tile_number = str(tile_id[0:2])
    tile_type = str(tile_id[2])
    tile_subtype = str(tile_id[3:5])
    return "/".join(["L2/tiles", tile_number, tile_type, tile_subtype, f"{title}.SAFE"])
