from shapely.geometry import Polygon
from typer.testing import CliRunner

from greensenti.cli.raster import project_shape


def test_projected_shape_is_valid_with_default_arguments():
    geom = {"type": "Polygon", "coordinates": [[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]]}
    projected = project_shape(geom)
    assert type(projected) is Polygon
