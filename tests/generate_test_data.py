import numpy as np
import rasterio
from rasterio.crs import CRS

out_meta = {
    "driver": "JP2OpenJPEG",
    "dtype": "uint16",
    "nodata": np.nan,
    "width": 1,
    "height": 1,
    "count": 1,
    "crs": CRS().from_epsg(32630),
    "transform": rasterio.Affine(10.0, 0.0, 365540.0, 0.0, -10.0, 4066920.0),
}

with rasterio.open("B1.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[1]]]))

with rasterio.open("B2.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[2]]]))

with rasterio.open("B3.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[3]]]))

out_meta.update({"height": 2, "width": 2})

with rasterio.open("B11.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[1, 1], [1, 1]]]))

with rasterio.open("B22.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[2, 2], [2, 2]]]))

with rasterio.open("B33.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[3, 3], [3, 3]]]))

with rasterio.open("B12.jp2", "w", **out_meta) as dest:
    dest.write(np.array([[[1, -1], [-1, 1]]]))
