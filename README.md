# greensenti

![CI](https://github.com/benhid/greensenti/actions/workflows/ci.yml/badge.svg)
![Release](https://github.com/benhid/greensenti/actions/workflows/release.yml/badge.svg)
<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

## Setup

From PyPI:

```console
$ pip install greensenti
$ pip install greensenti[gcloud] # For support to download from Google Cloud storage
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

     download
```
#### Download Sentinel-2 products

```console
$ greensenti download --help
$ greensenti download by-geometry geojson/teatinos.geojson 2022-10-01 2022-10-10
$ greensenti download by-geometry geojson/teatinos.geojson 2022-10-01 2022-10-10 --unzip --max_clouds 15 --output /tmp
$ greensenti download by-title S2B_MSIL2A_20221005T105819_N0400_R094_T30SUF_20221005T135951
$ greensenti download by-title '*T30SUF*' --from_date 2022-10-01 --to_date 2022-10-10 --unzip --max_clouds 15 --output /tmp
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
