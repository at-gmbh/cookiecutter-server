# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/at-gmbh/cookiecutter-server/compare/v1.0.0...HEAD)

- ...
## [1.2.2](https://github.com/at-gmbh/cookiecutter-server/tree/v1.2.2) - 2025-02-21

### 🐛 Bug Fixes
- Fixed an issue where `cc_server` would throw an `IndexError: tuple index out of range` when handling file paths in `is_change_relevant()`
- Prevented multiple consecutive updates from triggering when `cookiecutter-server.yml` is changed

## [1.2.1](https://github.com/at-gmbh/cookiecutter-server/tree/v1.2.1) - 2025-02-21
- fix version and issues in the deploy-yml and release.yml

## [1.2.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.2.0) - 2025-02-20
- Migrate poetry instead of pip and setup.py
- increase dependency version
- update python version
- fix unit tests while locally developing on mac


## [1.1.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.1.0) - 2023-01-20

- [#2](https://github.com/at-gmbh/cookiecutter-server/pull/2): Update dependencies, ignore changes to irrelevant files, fix minor issues

## [1.0.0](https://github.com/at-gmbh/cookiecutter-server/tree/v1.0.0) - 2021-09-03

- This is the first release of cookiecutter-server
- Created Python module `cc_server` with command line interface
- Release on [PyPI](https://pypi.org/project/cookiecutter-server/)
