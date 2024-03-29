import fire

import greensenti.band_arithmetic as ba
from greensenti import dhus, raster


def cli():
    cli_map = {
        "band-arithmetic": {
            "cloud-mask": ba.cloud_mask,
            "cloud-cover-percentage": ba.cloud_cover_percentage,
            "evi": ba.evi,
            "tc": ba.true_color,
            "ndwi": ba.ndwi,
            "ndsi": ba.ndsi,
            "moisture": ba.moisture,
            "bri": ba.bri,
            "cri1": ba.cri1,
            "evi2": ba.evi2,
            "mndwi": ba.mndwi,
            "ndre": ba.ndre,
            "ndvi": ba.ndvi,
            "ndyi": ba.ndyi,
            "osavi": ba.osavi,
        },
        "raster": {"apply-mask": raster.apply_mask, "transform-image": raster.transform_image},
        "download": {
            "by-title": dhus.download_by_title,
            "by-geometry": dhus.download_by_geometry,
        },
    }
    fire.Fire(cli_map)


if __name__ == "__main__":
    cli()
