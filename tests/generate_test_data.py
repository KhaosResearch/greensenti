from pathlib import Path

from greensenti.cli.raster import apply_mask

data_dir = Path("data")
product_safe_dir = (
    data_dir
    / "S2B_MSIL2A_20210103T110349_N0214_R094_T30SUF_20210103T130742/S2B_MSIL2A_20210103T110349_N0214_R094_T30SUF_20210103T130742.SAFE"
)

output_dir = Path("tests/data")
geojson = output_dir / "box.geojson"

for image in product_safe_dir.glob("GRANULE/*/IMG_DATA/**/*.jp2"):
    apply_mask(
        image,
        geojson=geojson,
        output=output_dir / image.name[-11:],
    )
