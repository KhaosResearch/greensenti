import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List

from sentinelsat.sentinel import SentinelAPI, geojson_to_wkt, read_geojson

try:
    GCLOUD_DISABLED = False
    from google.cloud import storage
except:
    GCLOUD_DISABLED = True

def download(
    geojson: Path,
    from_date: datetime,
    to_date: datetime,
    *,
    unzip: bool = False,
    output: Path = Path("."),
    dhus_username: str = os.environ.get("DHUS_USERNAME", None),
    dhus_password: str = os.environ.get("DHUS_PASSWORD", None),
    dhus_host: str = os.environ.get("DHUS_HOST", None),
    gcloud: Path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None),

):
    """
    Downloads products from D-HUS (Data Hub Software).

    :param geojson: GeoJSON file with product geometries.
    :param from_date: From date %Y-%m-%d (begin date).
    :param to_date: To date %Y-%m-%d (end date).
    :param output: Output folder.
    :param skip_unzip: Whether to skip product unzip.
    :return:
    """
    if gcloud and GCLOUD_DISABLED:
        print("Error: Missing required Google Cloud dependencies to download from GCloud, use `pip install greensenti[gcloud]` to install them.")
        exit(1)
    # Load geojson file* and download products for an interval of dates.
    #  *see: http://geojson.io/
    geojson = read_geojson(geojson)
    footprint = geojson_to_wkt(geojson)

    sentinel_api = SentinelAPI(dhus_username, dhus_password, dhus_host, show_progressbars=False)

    print("Searching for products in scene")

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

    if not gcloud:
        product_infos, triggered, failed_downloads = copernicous_download(ids, sentinel_api, output=output)
    else:
        gcloud_api = gcloud_bucket()
        # Google cloud doesn't utilize ids, only titles
        titles = products_df["title"]
        product_infos, triggered, failed_downloads = gcloud_download(titles, gcloud_api, output=output)
        

    print(f"Success: {len(product_infos)}")
    print(f"Triggered: {len(triggered)}")
    print(f"Failed: {len(failed_downloads)}")

    if unzip:
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


def copernicous_download(ids: List[str], api: SentinelAPI, output: Path = Path(".")) -> None:
    # Download products.
    product_infos, triggered, failed_downloads = api.download_all(
        ids, str(output), max_attempts=10, n_concurrent_dl=1, lta_retry_delay=600
    )
    return product_infos, triggered, failed_downloads

def gcloud_bucket():
    client = storage.Client()
    return client.bucket("gcp-public-data-sentinel-2")

def gcloud_download(titles: str, api: storage.Bucket, output: Path = Path(".")):
    product_infos = {}
    failed_downloads = {}

    for title in titles:
        try:
            gcloud_path = get_gcloud_path(title)
            product_folder = os.path.basename(gcloud_path)

            blobs = api.list_blobs(prefix=gcloud_path)

            for blob in blobs:
                if blob.name.endswith("/") or blob.name.endswith("$folder$"): # Ignore folders and GCloud files
                    continue

                # make sure temporal folder exists
                local_blob_dir = os.path.dirname(blob.name.removeprefix(gcloud_path+"/"))
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
            if not os.path.isfile(local_zip_file+".zip"):
                shutil.make_archive(local_zip_file, 'zip', local_product_folder)

            product_infos[title] = "OK"
        except Exception as e:
            failed_downloads[tile] = e

    return product_infos, {}, failed_downloads

def get_gcloud_path(title: str):
    """
    Gets the google cloud bucket prefix for a given Sentinel-2 product.
    Products are group by tile id or MGRS coordinatesor

    :param title: Sentinel-2 title.

    :return: Google Cloud path for title
    """
    tile_id = title.split("_T")[1] # This is always a 2 digit and 3 letter ID  E.g: 30SUF
    tile_number = str(tile_id[0:2])
    tile_type = str(tile_id[2])
    tile_subtype=str(tile_id[3:5])
    return "/".join(["L2/tiles", tile_number, tile_type, tile_subtype, f"{title}.SAFE"])