# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 0.7.0

### Added

- Add `skip` parameter to download functions to remove specific products from the query results.
- Add `override_no_data` parameter to mask functions, useful if you want to mask on a different value to the nodata specify in the kwargs.
- Include `ruff` linter and `pytest-cov` to the CI pipeline.
- Remove `setup.py` and `setup.cfg` in favour of `pyproject.toml`.

### Changes

- Download functions on the `dhus` module are now generators of dictionaries instead of a complete dataframe at the end of the download. This allow to each product to be process before the download of all of them is complete.
- Changed JSON representation of dates from epoch to ISO 8601.
- Changed behaviour of `band_arithmetic.cloud_mask` to return a GeoTiff instead of a .jp2
- `crop_by_shape`, `save_as_img` and `transform_image` no longer returns the output path.

### Removed

- The `unzip` parameter from the `dhus` module has been removed. This now defaults to true to maintain consistency between copernicous and gcloud downloads.

## 0.6.0

### Added

- Support to download Sentinel-2 products from Google Cloud storage.
- Added support to download by text match.
- Added `download by-geometry` and `download by-title` to Fire commands.

### Changes

- Ownership of the project transferred from [benhid](https://github.com/benhid/greensenti) to [Khaos Research](https://github.com/KhaosResearch/greensenti) organization on GitHub 🎉 

## Released

## 0.5.1

### Fixed

- True color image returning wrong shape

## 0.5.0

### Added

- BSI index implementation.

### Fixed

- Inconsistency between returned band and the band written to disk. More details in [#13](https://github.com/KhaosResearch/greensenti/pull/13#issuecomment-1278654643). 

## 0.4.0

### Added

- Start using changelog.

### Changes

- Package has been restructured to follow best practices (eg, now inside `src`).
- Modules from `greensenti.cli` sub-package has been moved to the top level.
- [`Typer`](https://typer.tiangolo.com) has been replaced by [`fire`](https://github.com/google/python-fire). 
There may be some limitations compared to `Typer` (eg, [path validations](https://typer.tiangolo.com/tutorial/parameter-types/path/#path-validations)), but now pure Python functions are fully decoupled from the client code.

### Removed

- Poetry is no loger used for dependency management and packaging.
