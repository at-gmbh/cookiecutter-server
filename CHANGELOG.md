# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/at-gmbh/cookiecutter-server/compare/v1.0.0...HEAD)

- ...


## [1.2.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.1.0) - 2025-02-19

### 🚀 Features
- Added support for Python 3.12 and 3.13
- Updated GitHub Actions workflows (`build.yml`, `deploy.yml`, `release.yml`) to use Python 3.9
- Upgraded dependencies, including:
  - `cookiecutter` to `~=2.5.0`
  - `typer` to `~=0.9.0`
  - `watchdog` to `~=3.0.0`
  - `dirsync` to `~=2.2.5`
  - `PyYAML` to `~=6.0`
  - `pre-commit` to `~=3.6`
  - `pytest` to `~=7.4`
  - `flake8` to `~=6.1`

### 🐛 Bug Fixes
- Fixed an issue where `cc_server` would throw an `IndexError: tuple index out of range` when handling file paths in `is_change_relevant()`
- Prevented multiple consecutive updates from triggering when `cookiecutter-server.yml` is changed

### 🔧 Maintenance
- Removed support for Python 3.7 and 3.8 (both are end-of-life)
- Improved workflow efficiency by upgrading to `actions/checkout@v4`, `setup-python@v5`, and `upload-artifact@v4`
- Updated `.github/workflows` to follow modern best practices

**Breaking Changes:**  
- Dropped support for Python 3.7 and 3.8  
- The minimal required Python version is now **3.9**

---


## [1.1.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.1.0) - 2023-01-20

- [#2](https://github.com/at-gmbh/cookiecutter-server/pull/2): Update dependencies, ignore changes to irrelevant files, fix minor issues

## [1.0.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.0.0) - 2021-09-03

- This is the first release of cookiecutter-server
- Created Python module `cc_server` with command line interface
- Release on [PyPI](https://pypi.org/project/cookiecutter-server/)
