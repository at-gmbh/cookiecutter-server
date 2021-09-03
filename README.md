# cookiecutter-server

[![build](https://img.shields.io/github/workflow/status/at-gmbh/cookiecutter-server/build)](https://github.com/at-gmbh/cookiecutter-server/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/cookiecutter-server)](https://pypi.org/project/cookiecutter-server/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cookiecutter-server)](https://pypi.org/project/cookiecutter-server/)
[![PyPI - License](https://img.shields.io/pypi/l/personio-py)](https://github.com/at-gmbh/cookiecutter-server/blob/master/LICENSE)

A local development server to get live previews of [cookiecutter templates](https://github.com/cookiecutter/cookiecutter).

Are there too many code paths in your cookiecutter templates? You need an easy way to check what your template looks like with different parameters? cookiecutter-server got you covered! It's a process that watches the source folder of your template and serves the rendered template in a different folder. Whenever you make a change in your template or select different parameters, the rendered template gets updated automatically.

## Getting Started

Install cookiecutter-server with

    pip install cookiecutter-server

This will make the `cc_server` command available on your terminal. Test it with

    cc_server --help

In case the command was not registered, you can use `python -m cc_server` instead.

Now switch to your cookiecutter template folder and run

    cc_server .

This will launch cookiecutter-server in the current folder and render the template in a new folder named `serve` under the current folder. Of course, you can also provide custom paths, if you prefer:

    cc_server path/to/cookiecutter -o path/to/output

The server process will now watch your template folder for changes. Please make a change in one of your template files and save the file. On the terminal, cc_server will tell you

> updating due to change in {changed file}

Now open this file in the output folder; your changes have already been applied. If you don't see the changes, please re-open the file or use an editor that automatically updates files when they change on disk, like PyCharm or VSCode.

How do you change your template parameters? In your cookiecutter template folder, a new file named `cookiecutter-server.yml` was created, which contains all the parameters of your template. Change the parameters to your liking and save the file, cookiecutter-server will immediately update the contents of the output folder.

To stop the server, use Ctrl+C on your terminal.

If you're having trouble with cookiecutter-server, please have a look at the [open issues](https://github.com/at-gmbh/cookiecutter-server/issues) and open a new one, if you can't find a solution.

## Contributing

To set up your local development environment, please use a fresh virtual environment, then run:

    pip install -r requirements.txt -r requirements-dev.txt
    pip install -e .

You can now launch the server from the command line; try `cc_server --help`.

We use `pytest` as test framework. To execute the tests, please run

    python setup.py test

To build a distribution package (wheel), please use

    python setup.py dist

this will clean up the build folder and then run the `bdist_wheel` command.

Before contributing code, please set up the pre-commit hooks to reduce errors and ensure consistency

    pip install -U pre-commit
    pre-commit install

### PyPI Release

This project is released on [PyPI](https://pypi.org/project/cookiecutter-server/). Most of the tedious steps that are required to test & publish your release are automated by [CI pipelines](https://github.com/at-gmbh/cookiecutter-server/actions). All you have to do is to write your code and when the time comes to make a release, please follow these steps:

* update the program version in [`src/cc_server/version.py`](./src/cc_server/version.py)
* write a summary of your changes in [`CHANGELOG.md`](./CHANGELOG.md)
* add a tag on the master branch with the new version number preceded by the letter `v`, e.g. for version 1.0.0 the tag would be `v1.0.0`. To tag the head of the current branch, use `git tag v1.0.0`
* push your changes to GitHub and don't forget to push the tag with `git push origin v1.0.0`
* now have a look at the [release pipeline](https://github.com/at-gmbh/cookiecutter-server/actions/workflows/release.yml); if it finishes without errors, you can find your release on [TestPyPI](https://test.pypi.org/project/cookiecutter-server/). Please verify that your release works as expected.
* Now for the live deployment on PyPI. To avoid mistakes, this is only triggered, when a release is published on GitHub first. Please have a look at the [Releases](https://github.com/at-gmbh/cookiecutter-server/releases) now; there should be a draft release with your version number (this was created by the CI pipeline which also made the TestPyPI release). Edit the draft release, copy the text you added to [`CHANGELOG.md`](./CHANGELOG.md) into the description field and publish it.
* After you publish the release, the [deploy pipeline](https://github.com/at-gmbh/cookiecutter-server/actions/workflows/deploy.yml) is triggered on GitHub. It will publish the release directly to [PyPI](https://pypi.org/project/cookiecutter-server/) where everyone can enjoy your latest features.

## Contact

Sebastian Straub (sebastian.straub [at] alexanderthamm.com)

Developed with ❤ at [Alexander Thamm GmbH](https://www.alexanderthamm.com/)

## License

    Copyright 2021 Alexander Thamm GmbH

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
