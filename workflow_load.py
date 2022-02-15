import glob
import zipfile
from datetime import datetime
from pathlib import Path, PosixPath

import pandas as pd
import simplejson as json

from greensenti.cli.compute_index import *
from greensenti.cli.dhus import download
from greensenti.cli.raster import apply_mask, transform_image

geojson = Path("geojson/ejido.geojson")
from_date = datetime.strptime("2021-01-01", "%Y-%m-%d")
to_dxate = datetime.strptime("2021-01-05", "%Y-%m-%d")

# This is the folder where the products are downloaded and processed.
output = Path("./data")
output.mkdir(exist_ok=True)

# Download products info or use cached ones if they exist.
if not (output / "product_infos.csv").is_file():
    product_infos, _, _ = download(
        geojson=geojson,
        from_date=from_date,
        to_date=to_date,
        output=output,
        skip_unzip=False,
    )
    product_infos = pd.DataFrame.from_dict(product_infos, orient="index")
    product_infos.to_csv(output / "product_infos.csv")
else:
    product_infos = pd.read_csv(output / "product_infos.csv")


def to_minio(src, dst):
    # TODO: use minio client
    return "minio://" + dst


# Process each product.
for _, product_info in product_infos.iterrows():
    product_as_dict = dict()
    product_as_dict.setdefault("indices", [])

    # Append metadata.
    product_as_dict["id"] = product_info["id"]
    product_as_dict["title"] = product_info["title"]
    product_as_dict["size"] = product_info["size"]
    product_as_dict["date"] = product_info["date"]
    product_as_dict["creationDate"] = product_info["Creation Date"]
    product_as_dict["ingestionDate"] = product_info["Ingestion Date"]

    # Product paths.
    title = product_as_dict["title"]

    product_dir = output / title
    product_zip = product_dir.with_suffix(".zip")  # zip file
    product_safe_dir = product_dir / Path(title + ".SAFE")  # uncompressed folder

    # Upload product.zip to MinIO.
    object_name = to_minio(src=product_zip, dst=f"products_S2A/{title}/{product_zip.name}")
    product_as_dict["objectName"] = object_name

    # Upload band images to MinIO.

    # quick check: We assume that the product is already downloaded and unzipped,
    # but this might not always be the case.
    if not product_safe_dir.is_dir():
        with zipfile.ZipFile(product_zip, "r") as zip_file:
            zip_file.extractall(product_dir)

    for image in product_safe_dir.glob("GRANULE/*/IMG_DATA/**/*.jp2"):
        to_minio(src=image, dst=f"products_S2A/{title}/{image.name}")

    product_as_dict["bands"] = f"minio://products_S2A/{title}/raw/"

    # Upload to MongoDB.
    print(json.dumps(product_as_dict, indent=2, default=str))
    # TODO
