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
  compute-index  Compute a plethora of remote sensing indexes.
  dhus           DHUS access and download.
  raster         Raster operations.
```

### Tutorial

##### Compute NDVI of El Ejido district (Málaga)

```console
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/ejido.geojson
$ greensenti raster apply-mask --output B08_10m_masked.jp2 examples/B08_10m.jp2 geojson/ejido.geojson
$ greensenti compute-index ndvi --help
Usage: greensenti compute-index ndvi [OPTIONS] B4 B8

  Compute Normalized Difference Vegetation Index (NDVI).
  
Arguments:
  B4  RED band (B04 for Sentinel-2, 10m)  [required]
  B8  NIR band (B08 for Sentinel-2, 10m)  [required]

Options:
  --output PATH  Output file
  --help         Show this message and exit.
$ greensenti compute-index ndvi --output ndvi.tif B04_10m_masked.jp2 B08_10m_masked.jp2
$ greensenti raster transform-image --output ndvi.png --cmap RdYlBu ndvi.tif
```

<img src="resources/ndvi.png" height="200" />

##### Compute true color of Teatinos Campus (University of Málaga)

```console
$ greensenti raster apply-mask --output B02_10m_masked.jp2 examples/B02_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B03_10m_masked.jp2 examples/B03_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/teatinos.geojson
$ greensenti compute-index true-color --output true-color.tif B04_10m_masked.jp2 B03_10m_masked.jp2 B02_10m_masked.jp2
$ greensenti raster transform-image --output true-color.png true-color.tif
```

<img src="resources/true-color.png" height="200" />
