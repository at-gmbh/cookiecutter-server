import os
import shutil
import subprocess
import sys
from distutils.cmd import Command
from pathlib import Path
from runpy import run_path

from setuptools import find_packages, setup

# read the program version from version.py (without loading the module)
__version__ = run_path('src/cc_server/version.py')['__version__']


def read(fname):
    """Utility function to read the README file."""
    return (Path(__file__).parent / fname).read_text('utf-8')


class DistCommand(Command):

    description = "build the distribution packages (in the 'dist' folder)"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"])


class TestCommand(Command):

    description = "run all tests with pytest"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        sys.path.append('src')
        import pytest
        return pytest.main(['tests', '--no-cov'])


class TestCovCommand(Command):

    description = "run all tests with pytest and write a test coverage report"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        sys.path.append('src')
        params = "tests --doctest-modules --junitxml=junit/test-results.xml " \
                 "--cov=src --cov-report=xml --cov-report=html --cov-report=term"
        import pytest
        return pytest.main(params.split(' '))


setup(
    name="cookiecutter-server",
    version=__version__,
    author="Sebastian Straub",
    author_email="sebastian.straub@alexanderthamm.com",
    description="A local development server to get live previews of cookiecutter templates",
    license="Apache License 2.0",
    url="https://github.com/at-gmbh/cookiecutter-server",
    project_urls={
        'Source': 'https://github.com/at-gmbh/cookiecutter-server',
        'Tracker': 'https://github.com/at-gmbh/cookiecutter-server/issues',
    },
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={'console_scripts': ['cc_server = cc_server.main:app']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=[
        'typer[all]>=0.6,<1.0',
        'cookiecutter>=1.7.2',
        'watchdog>=2.2,<3.0',
        'dirsync>=2.2,<3.0',
        'PyYAML>=5.0,<7.0',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pre-commit',
    ],
    cmdclass={
        'dist': DistCommand,
        'test': TestCommand,
        'testcov': TestCovCommand,
    },
    platforms='any',
    python_requires='>=3.7',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
