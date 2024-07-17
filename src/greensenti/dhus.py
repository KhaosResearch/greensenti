import json
import os
import re
import warnings
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Union

import geomet.wkt
import pandas as pd
import requests

import geojson

try:
    GCLOUD_DISABLED = False
    from google.cloud import storage
except ImportError:
    GCLOUD_DISABLED = True
    storage = None


def to_wkt(geojson_file: Path, decimals: int = 4) -> str:
    with open(geojson_file) as f:
        geojson_ = geojson.load(f)

    # Extract geometry from GeoJSON
    geometry = geojson_["features"][0]["geometry"]

    wkt = geomet.wkt.dumps(geometry, decimals=decimals)
    # Strip unnecessary spaces
    wkt = re.sub(r"(?<!\d) ", "", wkt)
    return wkt


def get_metadata_cdse(footprint: str, from_date: str, to_date) -> pd.DataFrame:
    """
    Downloads metadata from the Copernicus Data Space Ecosystem (CDSE) API.

    :param footprint: Footprint in WKT format.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :return: DataFrame with metadata
    """
    response = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-2' and contains(Name,'MSIL2A') and OData.CSC.Intersects(area=geography'SRID=4326;{footprint}') and ContentDate/Start gt {from_date}T00:00:00.000Z and ContentDate/Start lt {to_date}T00:00:00.000Z&$top=1000"
    ).json()

    products_df = pd.DataFrame.from_dict(response["value"])
    products_df["title"] = products_df["Name"]

    return products_df


def download_by_title(
    text_match: str,
    from_date: str | datetime = None,
    to_date: str | datetime = None,
    *,
    max_clouds: int = 100,
    output: Path = Path("."),
    skip: List[str] = None,
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> Iterator[dict]:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud by a text match with the product title.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param text_match: Regular expresion to match the product filename.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param output: Output folder.
    :param skip: List of product titles to ignore
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: Yields an iterator of dictionaries with the product metadata and download status
    """
    yield from download(
        geojson_file=None,
        text_match=text_match,
        from_date=from_date,
        to_date=to_date,
        max_clouds=max_clouds,
        output=output,
        skip=skip,
        dhus_username=dhus_username,
        dhus_password=dhus_password,
        dhus_host=dhus_host,
        gcloud=gcloud,
    )


def download_by_geometry(
    geojson_file: Path,
    from_date: Union[str, datetime] = None,
    to_date: Union[str, datetime] = None,
    *,
    max_clouds: int = 100,
    output: Path = Path("."),
    skip: List[str] = None,
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> Iterator[dict]:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud by a given geometry in GeoJSON format.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param geojson_file: GeoJSON file with product geometries.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param output: Output folder.
    :param skip: List of product titles to ignore
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: Yields an iterator of dictionaries with the product metadata and download status
    """
    yield from download(
        geojson_file=geojson_file,
        text_match=None,
        from_date=from_date,
        to_date=to_date,
        max_clouds=max_clouds,
        output=output,
        skip=skip,
        dhus_username=dhus_username,
        dhus_password=dhus_password,
        dhus_host=dhus_host,
        gcloud=gcloud,
    )


def download(
    geojson_file: Path = None,
    text_match: str | None = "*",
    from_date: Union[str, datetime] = None,
    to_date: Union[str, datetime] = None,
    *,
    max_clouds: int = 100,
    output: Path = Path("."),
    skip: list[str] = None,
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),
) -> Iterator[dict]:
    """
    Downloads Sentinel-2 products from DHuS (Data Hub Service) or Google Cloud.

    To connect to Google Cloud to download Sentinel-2 data the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :param geojson_file: GeoJSON file with product geometries.
    :param text_match: Regular expresion to match the product filename.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param max_clouds: Max cloud percentage.
    :param output: Output folder.
    :param skip: List of product titles to ignore
    :param dhus_username: Username from dhus service. Taken from enviroment as DHUS_USERNAME if available.
    :param dhus_password: Password from dhus service. Taken from enviroment as DHUS_PASSWORD if available.
    :param dhus_host: Host from dhus service. Taken from enviroment as DHUS_HOST if available.
    :param gcloud: Google Cloud credentials file. Taken from enviroment as GOOGLE_APPLICATION_CREDENTIALS if available.
    :return: Yields an iterator of dictionaries with the product metadata and download status
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

    if isinstance(output, str):
        output = Path(output)

    # When using dataspace,they must be string
    from_date = datetime.strftime(from_date, "%Y-%m-%d")
    to_date = datetime.strftime(to_date, "%Y-%m-%d")

    # Load geojson file* and download products for an interval of dates.
    #  *see: http://geojson.io/
    if geojson_file:
        footprint = to_wkt(geojson_file)
    else:
        footprint = None

    # Text match uses filename, to avoid users having to add unknown extensions,
    # add wildcard at the end
    if text_match:
        warnings.warn(
            """Text matching is still not supported for the new CDSE API and is being worked on.
More detail can be read here: https://dataspace.copernicus.eu/news/2023-9-28-accessing-sentinel-mission-data-new-copernicus-data-space-ecosystem-apis""",
            DeprecationWarning,
            stacklevel=2,
        )

        if not text_match.endswith("*"):
            text_match += "*"

    products_df = get_metadata_cdse(footprint, from_date, to_date)

    if skip:
        products_df = products_df[~products_df["title"].isin(skip)]
    ids = products_df.index

    print(f"Found {len(ids)} scenes between {from_date} and {to_date}")

    if not gcloud:
        # WIP: add support for new CDSE
        warnings.warn(
            """This method is no longer works, support for the new CDSE API is being worked on.
More detail can be read here: https://dataspace.copernicus.eu/news/2023-9-28-accessing-sentinel-mission-data-new-copernicus-data-space-ecosystem-apis""",
            DeprecationWarning,
            stacklevel=2,
        )
    else:
        gcloud_api = gcloud_bucket()
        # Google cloud doesn't utilize ids, only titles
        titles = products_df["title"]
        for product in gcloud_download(titles, gcloud_api, output=output):
            product_json_str = products_df[products_df["title"] == product["title"]].to_json(
                orient="records", date_format="iso"
            )
            product_json = json.loads(product_json_str)[0]  # Pandas gives a list of elements always
            yield {**product_json, **product}


def unzip_product(output_folder: Path, title: str) -> None:
    """
    Unzip a downloaded product inside the same folder

    :param output_folder: Output folder.
    :param title: Sentinel-2 product title.

    :return: None
    """
    # Make sure the output folder exists.
    data_dir = Path(output_folder, title)
    data_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = Path(output_folder, title + ".zip")

    # We assume the file is already unzip correctly
    if Path(data_dir, title).is_dir():
        return

    with zipfile.ZipFile(zip_filename, "r") as zip_file:
        zip_file.extractall(data_dir)


def gcloud_bucket() -> "storage.Client":
    """
    Connects to Google Cloud and returns the client object
    Sentinel-2 data.

    **Expects** the enviroment variable GOOGLE_APPLICATION_CREDENTIALS to be set
    as defined here https://googleapis.dev/python/google-api-core/latest/auth.html#overview.

    :return: Google Cloud client object
    """
    client = storage.Client()
    return client


def gcloud_download(titles: List[str], api: "storage.Client", output: Path = Path(".")) -> Iterator[dict]:
    """
    Downloads a list of Sentinel-2 products by a list of titles from Google Cloud.

    :param titles: Sentinel-2 product titles.
    :param api: Google Cloud client object.
    :param output: Output folder.
    :return: Yields an iterator of dictionaries with the product status
    """

    for title in titles:
        try:
            gcloud_path = get_gcloud_path(title.removesuffix(".SAFE"))
            product_folder = Path(gcloud_path).name.removesuffix(".SAFE")

            blobs = api.list_blobs("gcp-public-data-sentinel-2", prefix=gcloud_path)

            for blob in blobs:
                if blob.name.endswith("/") or blob.name.endswith("$folder$"):  # Ignore folders and GCloud files
                    continue

                # Prepare path to local file
                output_folder = output.resolve() / product_folder
                local_blob_name = Path(blob.name.removeprefix(gcloud_path + "/"))
                local_blob_path = output_folder / local_blob_name

                # Make sure output folder exists
                local_blob_path.parent.mkdir(parents=True, exist_ok=True)

                # Download if doesn't exist
                if not Path.is_file(local_blob_path):
                    blob.download_to_filename(local_blob_path)
                else:
                    print("File exists, skipping")

            yield {
                "title": title,
                "status": "ok",
            }
        except Exception as e:
            yield {
                "title": title,
                "status": "failed",
                "error": str(e),
            }


def get_gcloud_path(title: str) -> str:
    """
    Gets the Google cloud bucket prefix for a given Sentinel-2 product.
    Products are group by tile id or MGRS coordinates.

    :param title: Sentinel-2 title.
    :return: Google Cloud path for title.
    """
    tile_id = title.split("_T")[1]  # This is always a 2 digit and 3 letter ID  E.g: 30SUF
    tile_number = str(tile_id[0:2])
    tile_type = str(tile_id[2])
    tile_subtype = str(tile_id[3:5])
    return "/".join(["L2/tiles", tile_number, tile_type, tile_subtype, f"{title}.SAFE"])
