import json
from pathlib import Path
from typing import Tuple

import numpy as np
import pytest
import rasterio
from greensenti.raster import (
    apply_mask,
    crop_by_shape,
    project_shape,
    rescale_band,
    save_as_img,
    transform_image,
)
from rasterio import Affine
from rasterio.crs import CRS
from shapely.geometry import Polygon, box


@pytest.fixture
def raster(tmp_path: Path) -> Tuple[Path, np.ndarray]:
    """Create a temporary GeoTIFF raster for testing."""
    data = np.ones((3, 3), dtype=np.uint8)
    data[1, 1] = 0
    filepath = tmp_path / "test.tif"
    profile = {
        "driver": "GTiff",
        "width": 3,
        "height": 3,
        "count": 1,
        "dtype": np.uint8,
        "transform": rasterio.transform.from_bounds(0, 0, 3, 3, 1, 1),
        "crs": "EPSG:4326",
        "nodata": 255,
    }
    with rasterio.open(filepath, "w", **profile) as dst:
        dst.write(data, 1)
    return filepath, data


@pytest.fixture
def geojson(tmp_path: Path) -> Path:
    """Create a temporary GeoJSON file for testing."""
    filepath = tmp_path / "test.geojson"
    with open(filepath, "w") as f:
        json.dump(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "coordinates": [
                                [
                                    [0.5, 2.5],
                                    [0.5, -5.5],
                                    [8.5, -5.5],
                                    [8.5, 2.5],
                                    [0.5, 2.5],
                                ]
                            ],
                            "type": "Polygon",
                        },
                    }
                ],
            },
            f,
        )
    return filepath


def test_crop_by_shape(tmp_path: Path, raster: Tuple[Path, np.ndarray]):
    filename, data = raster
    shp = Polygon([(0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5)])
    output = tmp_path / "out.tif"
    crop_by_shape(filename, shp, str(output))
    with rasterio.open(output) as src:
        out_data = src.read(1)
        assert np.array_equal(out_data, [[1]])  # check cropped data matches expected output
        assert src.transform == rasterio.transform.from_bounds(0, 0, 3, 3, 1, 1)  # check transform is preserved
        assert src.nodata == 255  # check nodata value is preserved


def test_project_shape():
    geom = Polygon([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])
    scs = "epsg:4326"  # WGS84
    dcs = "epsg:32630"  # UTM Zone 30N
    projected_geom = project_shape(geom, scs, dcs)
    assert isinstance(projected_geom, Polygon)
    # Pre-computed expected coordinates from https://mygeodata.cloud/cs2cs/
    expected_coordinates = [
        (945193.8596723974, 221604.0105092727),
        (1167251.17456618, 444571.27572022245),
        (1388201.8128537573, 669718.2534930086),
        (1607445.2430325048, 897851.6826293071),
        (1824332.655764979, 1129761.3603107734),
        (945193.8596723974, 221604.0105092727),
    ]
    for (x1, y1), (x2, y2) in zip(projected_geom.exterior.coords, expected_coordinates, strict=True):
        assert round(x1, 1) == round(x2, 1)
        assert round(y1, 1) == round(y2, 1)


def test_save_as_img(tmp_path: Path):
    raster = np.random.rand(100, 200)
    output = tmp_path / "output.png"
    save_as_img(raster, output)
    assert output.is_file()
    assert output.stat().st_size > 0


def test_transform_image(tmp_path: Path, raster: Tuple[Path, np.ndarray]):
    input_file, _ = raster
    output_file = tmp_path / "transformed_image.png"
    transform_image(band=input_file, color_map=None, output=output_file)
    assert output_file.is_file()
    assert output_file.stat().st_size > 0


def test_apply_mask(tmp_path: Path, geojson: Path, raster: Tuple[Path, np.ndarray]):
    input_file, _ = raster
    output_file = tmp_path / "masked_image.tif"
    output_path = apply_mask(filename=input_file, geojson=geojson, geojson_crs="epsg:4326", output=output_file)
    assert output_path.is_file()
    assert output_path.stat().st_size > 0

    with rasterio.open(input_file) as src:
        original_bounds = src.bounds
        original_count = src.count

    with rasterio.open(output_path) as src:
        masked_bounds = src.bounds
        masked_count = src.count

    assert original_count == masked_count

    # Check if the masked image is within the bounds of the geojson file.
    assert box(*original_bounds).contains(box(*masked_bounds))


def test_rescale_band():
    input_band = np.zeros((3, 2, 2))
    input_kwargs = {
        "driver": "JP2OpenJPEG",
        "dtype": "uint16",
        "nodata": None,
        "width": 2,
        "height": 2,
        "count": 3,
        "crs": CRS({"init": "epsg:32618"}),
        "transform": Affine(20.0, 0.0, 0, 0.0, -20.0, 0),
    }
    output_band, output_kwargs = rescale_band(input_band, input_kwargs)
    assert output_kwargs["transform"][0] == 10 and output_kwargs["transform"][4] == -10  # check resolution is correct
    assert input_band.size * 2 * 2 == output_band.size  # check if the band is twice as big in each direction
