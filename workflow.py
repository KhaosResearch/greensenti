import glob
from datetime import datetime
from pathlib import Path, PosixPath

import pandas as pd
import simplejson as json

from greensenti.cli.compute_index import *
from greensenti.cli.download_products import dhus_download
from greensenti.cli.raster import apply_mask, transform_image

geojson = Path("geojson/ejido.geojson")
from_date = datetime.strptime("2021-01-01", "%Y-%m-%d")
to_date = datetime.strptime("2021-01-31", "%Y-%m-%d")
output = Path("./data")

# Download products or use cached ones if they exist
if not (output / "product_infos.csv").is_file():
    product_infos, _, _ = dhus_download(
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

# Process each product
for _, product_info in product_infos.iterrows():
    product_as_dict = dict()

    product_as_dict.setdefault("indices", dict())

    # Append product metadata
    product_as_dict["id"] = product_info["id"]
    product_as_dict["title"] = product_info["title"]
    product_as_dict["size"] = product_info["size"]
    product_as_dict["date"] = product_info["date"]
    product_as_dict["creationDate"] = product_info["Creation Date"]
    product_as_dict["ingestionDate"] = product_info["Ingestion Date"]

    # Product paths
    title = product_as_dict["title"]
    product_dir = output / title
    product_safe_dir = product_dir / Path(title + ".SAFE")

    product_as_dict["objectName"] = product_dir.with_suffix(".zip")

    def find_product_image(pattern: str) -> Path:
        """
        Finds image matching a pattern in the product folder with glob.

        :param pattern: A pattern to match.
        :return: A Path object pointing to the first found image.
        """
        return next(product_safe_dir.glob("GRANULE/*/IMG_DATA/**/" + pattern))

    def mask_images() -> dict:
        """
        Finds all images in the product folder and applies a mask to them.

        :return: A dictionary mapping the original image path to the masked one.
        """
        images = dict()
        for image in product_safe_dir.glob("GRANULE/*/IMG_DATA/**/*.jp2"):
            masked_image = apply_mask(
                image,
                geojson=geojson,
                output=product_dir / geojson.name / image.name,
            )
            images[masked_image.stem[-7:]] = masked_image
        return images

    images = mask_images()

    # Compute cloud cover percentage
    index_value = cloud_cover_percentage(b3=images["B03_20m"], b4=images["B04_20m"], b11=images["B11_20m"], tau=0.2)

    product_as_dict["indices"]["cover-percentage"] = dict(
        objectName=None,
        rawObjectName=None,
        band={"b3": images["B03_20m"], "b4": images["B04_20m"], "b11": images["B11_20m"]},
        mask={"name": geojson.name, "objectName": None},
        value=index_value,
    )

    if index_value > 0.5:
        print(f"{title} cloud cover percentage ({index_value}) above threshold, skipping")
        continue

    # True color composite
    try:
        true_color(
            r=images["B04_10m"],
            g=images["B03_10m"],
            b=images["B02_10m"],
            output=product_dir / geojson.name / "true_color.tiff",
        )

        transform_image(
            band=product_dir / geojson.name / "true_color.tiff",
            output=product_dir / geojson.name / "true_color.png",
            color_map=None,
        )

        product_as_dict["indices"]["true-color"] = dict(
            objectName=None,
            rawObjectName=None,
            band={"r": images["B04_10m"], "g": images["B03_10m"], "b": images["B02_10m"]},
            mask={"name": geojson.name, "objectName": None},
            value=None,
        )
    except Exception as e:
        print(f"{title} true color failed: {e}")

    # Compute moisture
    try:
        index_value = moisture(
            b8a=images["B8A_20m"],
            b11=images["B11_20m"],
            output=product_dir / geojson.name / "moisture.tiff",
        )

        transform_image(
            band=product_dir / geojson.name / "moisture.tiff",
            output=product_dir / geojson.name / "moisture.png",
            color_map=None,
        )

        product_as_dict["indices"]["true-color"] = dict(
            objectName=None,
            rawObjectName=None,
            band={"b8a": images["B8A_20m"], "b11": images["B11_20m"]},
            mask={"name": geojson.name, "objectName": None},
            value=index_value,
        )
    except Exception as e:
        print(f"{title} moisture failed: {e}")

    # Compute NDVI
    try:
        index_value = ndvi(
            b4=images["B04_10m"],
            b8=images["B08_10m"],
            output=product_dir / geojson.name / "ndvi.tiff",
        )

        transform_image(
            band=product_dir / geojson.name / "ndvi.tiff",
            output=product_dir / geojson.name / "ndvi.png",
            color_map="RdYlBu",
        )

        product_as_dict["indices"]["ndvi"] = dict(
            objectName=None,
            rawObjectName=None,
            band={"b4": images["B04_10m"], "b8": images["B08_10m"]},
            mask={"name": geojson.name, "objectName": None},
            value=index_value,
        )
    except Exception as e:
        print(f"{title} NDVI failed: {e}")

    # Compute NDWI
    try:
        index_value = ndwi(
            b3=images["B03_10m"],
            b8=images["B08_10m"],
            output=product_dir / geojson.name / "ndwi.tiff",
        )

        transform_image(
            band=product_dir / geojson.name / "ndwi.tiff", output=product_dir / geojson.name / "ndwi.png", color_map=None
        )

        product_as_dict["indices"]["ndwi"] = dict(
            objectName=None,
            rawObjectName=None,
            band={"b3": images["B03_10m"], "b8": images["B08_10m"]},
            mask={"name": geojson.name, "objectName": None},
            value=index_value,
        )
    except Exception as e:
        print(f"{title} NDWI failed: {e}")

    # Compute NDSI
    try:
        index_value = ndsi(
            b3=images["B03_20m"],
            b11=images["B11_20m"],
            output=product_dir / geojson.name / "ndsi.tiff",
        )

        transform_image(
            band=product_dir / geojson.name / "ndsi.tiff", output=product_dir / geojson.name / "ndsi.png", color_map=None
        )

        product_as_dict["indices"]["ndsi"] = dict(
            objectName=None,
            rawObjectName=None,
            band={"b3": images["B03_20m"], "b11": images["B11_20m"]},
            mask={"name": geojson.name, "objectName": None},
            value=index_value,
        )
    except Exception as e:
        print(f"{title} NDSI failed: {e}")

    # Compute EVI
    try:
        raw_object_name = product_dir / geojson.name / "evi.raw.tiff"
        object_name = product_dir / geojson.name / "evi.png"

        index_value = evi(
            b2=images["B02_10m"],
            b4=images["B04_10m"],
            b8=images["B08_10m"],
            output=raw_object_name,
        )

        transform_image(
            band=raw_object_name, output=object_name, color_map=None
        )

        product_as_dict["indices"]["evi"] = dict(
            objectName=object_name,
            rawObjectName=raw_object_name,
            band={"b2": images["B02_10m"], "b4": images["B04_10m"], "b8": images["B08_10m"]},
            mask={"name": geojson.name, "footprint": None},
            value=index_value,
        )
    except Exception as e:
        print(f"{title} EVI failed: {e}")

    print(json.dumps(product_as_dict, indent=2, default=str))
