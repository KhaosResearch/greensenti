# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## Released

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