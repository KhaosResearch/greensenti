## greensenti _toolbox_

![CI](https://github.com/benhid/greensenti/actions/workflows/ci.yml/badge.svg)
![Release](https://github.com/benhid/greensenti/actions/workflows/release.yml/badge.svg)
<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

### Setup

Using `pip`:

```console
$ pip install greensenti
```

Using Poetry:

```console
$ poetry install
```

### Usage

```console
$ poetry run greensenti --help
Usage: greensenti [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  band-arithmetic  Compute a plethora of remote sensing indexes.
  dhus             DHUS access and download.
  raster           Raster operations.
```

### Tutorial

##### Compute NDVI of El Ejido district (Málaga)

```console
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/ejido.geojson
$ greensenti raster apply-mask --output B08_10m_masked.jp2 examples/B08_10m.jp2 geojson/ejido.geojson
$ greensenti band-arithmetic ndvi --help
Usage: greensenti band-arithmetic ndvi [OPTIONS] B4 B8

  Compute Normalized Difference Vegetation Index (NDVI). Value ranges from -1
  to 1. Negative values correspond to water. Values close to zero (-0.1 to
  0.1) generally correspond to barren areas of rock, sand, or snow. Low,
  positive values represent shrub and grassland (approximately 0.2 to 0.4),
  while high values indicate temperate and tropical rainforests (values
  approaching 1).

Arguments:
  B4  RED - B04 band for Sentinel-2 (10m)  [required]
  B8  NIR - B08 band for Sentinel-2 (10m)  [required]

Options:
  --output PATH  Output file
  --help         Show this message and exit.
$ greensenti band-arithmetic ndvi --output ndvi.tif B04_10m_masked.jp2 B08_10m_masked.jp2
$ greensenti raster transform-image --output ndvi.png --cmap RdYlBu ndvi.tif
```

<img src="resources/ndvi.png" height="200" />

##### Compute true color of Teatinos Campus (University of Málaga)

```console
$ greensenti raster apply-mask --output B02_10m_masked.jp2 examples/B02_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B03_10m_masked.jp2 examples/B03_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/teatinos.geojson
$ greensenti band-arithmetic true-color --output true-color.tif B04_10m_masked.jp2 B03_10m_masked.jp2 B02_10m_masked.jp2
$ greensenti raster transform-image --output true-color.png true-color.tif
```

<img src="resources/true-color.png" height="200" />
