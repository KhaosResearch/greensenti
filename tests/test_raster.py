import numpy as np

from shapely.geometry import Polygon
from rasterio import Affine
from rasterio.crs import CRS

from greensenti.raster import project_shape, rescale_band


def test_projected_shape_is_valid_with_default_arguments():
    geom = {"type": "Polygon", "coordinates": [[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]]}
    projected = project_shape(geom)
    assert type(projected) is Polygon

def test_rescale_band_is_correct():
    input_band = np.zeros((3, 2, 2))
    input_kwargs = {
        'driver': 'JP2OpenJPEG',
        'dtype': 'uint16',
        'nodata': None,
        'width': 2,
        'height': 2,
        'count': 3,
        'crs': CRS({'init': 'epsg:32618'}),
        'transform': Affine(20.0, 0.0, 0, 0.0, -20.0, 0)
    }

    output_band, output_kwargs = rescale_band(input_band, input_kwargs)

    # Check if the resolution is correct
    assert output_kwargs['transform'][0] == 10 and output_kwargs['transform'][4] == -10

    # Check if the band is twice as big (doubling the resolution) in each direction
    assert input_band.size*2*2 == output_band.size