# greensenti

![CI](https://github.com/benhid/greensenti/actions/workflows/ci.yml/badge.svg)
![Release](https://github.com/benhid/greensenti/actions/workflows/release.yml/badge.svg)
<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Setup

From PyPI:

```console
$ pip install greensenti
```

From source code:

```console
$ python setup.py install
```

## Usage

Run with `-h` / `--help` to display help for the client itself or for any specific command:

```console
$ greensenti --help
NAME
    greensenti

SYNOPSIS
    greensenti GROUP

GROUPS
    GROUP is one of the following:

     band-arithmetic

     raster
```

#### Compute NDVI of El Ejido district (Málaga)

```console
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/ejido.geojson
$ greensenti raster apply-mask --output B08_10m_masked.jp2 examples/B08_10m.jp2 geojson/ejido.geojson
$ greensenti band-arithmetic ndvi --output ndvi.tif B04_10m_masked.jp2 B08_10m_masked.jp2
$ greensenti raster transform-image --output ndvi.png --cmap RdYlBu ndvi.tif
```

<img src="resources/ndvi.png" height="200" />

#### Compute true color composite of Teatinos Campus (University of Málaga)

```console
$ greensenti raster apply-mask --output B02_10m_masked.jp2 examples/B02_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B03_10m_masked.jp2 examples/B03_10m.jp2 geojson/teatinos.geojson
$ greensenti raster apply-mask --output B04_10m_masked.jp2 examples/B04_10m.jp2 geojson/teatinos.geojson
$ greensenti band-arithmetic true-color --output true-color.tif B04_10m_masked.jp2 B03_10m_masked.jp2 B02_10m_masked.jp2
$ greensenti raster transform-image --output true-color.png true-color.tif
```

<img src="resources/true-color.png" height="200" />

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.

## License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for more info.
