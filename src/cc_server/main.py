import json
import logging
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional, Union

import typer
import yaml
from cookiecutter.main import cookiecutter
from dirsync import sync
from rich import print
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from yaml import FullLoader

from cc_server import __title__, __version__

logging.basicConfig(format="%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
                    level=logging.WARNING)
logger = logging.getLogger('cc_server')
logger.setLevel(logging.WARNING)


app = typer.Typer(
    name='cc_server',
    help="A local development server to get live previews of cookiecutter templates")


def version_callback(version: bool):
    if version:
        print(f"{__title__} {__version__}")
        raise typer.Exit()


TemplatePath = typer.Argument(
    ...,
    help="cookiecutter template source folder",
    exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True)
OutputPath = typer.Option(
    './serve/', '-o', '--output',
    help="output folder (defaults to folder 'serve' under the current folder)",
    exists=False, file_okay=False, dir_okay=True, resolve_path=True)
Version = typer.Option(
    None, '-v', '--version', callback=version_callback, is_eager=True,
    help="print the program version and exit")


@app.command()
def main(template: Path = TemplatePath, output: Path = OutputPath, version: bool = Version):
    """
    A local development server to get live previews of cookiecutter templates
    """
    print(
        f"starting [yellow]cookiecutter-server[/yellow] "
        f"(template: '{template}', output: '{output}')")
    server = CookiecutterServer(
        template_dir=template,
        output_dir=output)
    server.serve()


class CookiecutterServer:
    """
    cookiecutter server: get live previews of cookiecutter templates while you're working on them.

    Creates an instance of the cookiecutter template in `template_dir` and writes it
    to `output_dir`. The settings for the template are specified by `config_file`, if provided,
    otherwise a file named `cookiecutter-server.yml` is generated in the template folder.

    Cookiecutter server is watching for changes in the template server. When a file is changed,
    the template will be rendered and all changed files will be updated in the output directory.
    The same applies for the config file: when you change a config parameter, the rendered
    template will be updated as well.

    :param template_dir: the folder where the cookiecutter template is located
           (must contain a cookiecutter.json or cookiecutter.yml)
    :param output_dir: the folder where the live preview shall be served
    :param config_file: settings for the cookiecutter template (default settings will be stored
           in cookiecutter-server.yml, when this file is not provided)
    :param min_delay: wait at least this many seconds, before the template will be rendered again
           (prevents high disk & cpu load when changes are detected in quick succession)
    """

    default_config = 'cookiecutter-server.yml'
    template_files = [
        ('cookiecutter.json', json),
        ('cookiecutter.yml', yaml),
        ('cookiecutter.yaml', yaml),
    ]

    def __init__(self, template_dir: Path, output_dir: Path, config_file: Path = None,
                 min_delay=5.0):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.config_file = self._init_config(template_dir, config_file)
        self.observer = Observer()
        self.handler = TemplateUpdate(
            self.template_dir, self.output_dir, self.config_file, min_delay)
        self.signal_stop = False

    def serve(self):
        # render the template for the first time, if the output directory does not exist
        if not self.output_dir.is_dir():
            self.handler.render_template(self.output_dir)
        # start the watchdog
        self.observer.schedule(self.handler, self.template_dir, recursive=True)
        self.observer.start()
        print("template is ready, watching for changes")
        try:
            while not self.signal_stop:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.observer.stop()
            self.observer.join(1.0)
        print("[yellow]cookiecutter-server[/yellow] terminated")

    @classmethod
    def _init_config(cls, template_dir: Path, config_file: Path = None):
        # check if a config file is defined
        if config_file is None:
            config_file = template_dir / cls.default_config
        # validate the existing config or generate a new one
        if config_file.is_file():
            with config_file.open() as fp:
                yaml.load(fp, Loader=FullLoader)
        else:
            cls._fill_config(template_dir, config_file)
        logger.info(f"your template config is at {config_file}")
        return config_file

    @classmethod
    def _fill_config(cls, template_dir: Path, config_file: Path):
        for fname, parser in cls.template_files:
            path = template_dir / fname
            if path.exists():
                with path.open('r') as fp:
                    cc_config = parser.load(fp)
                ccs_config = {k: v[0] if isinstance(v, list) else v for k, v in cc_config.items()}
                with config_file.open('w') as fp:
                    yaml.dump(ccs_config, fp, sort_keys=False)
                return config_file
        raise RuntimeError(f"No cookiecutter.json found in {template_dir}")


class TemplateUpdate(FileSystemEventHandler):
    """
    ...

    :param template_dir: the folder where the cookiecutter template is located
    :param output_dir: the folder where the live preview shall be served
    :param config_file: settings for the cookiecutter template
    :param min_delay: wait at least this many seconds, before the template will be rendered again
    """

    def __init__(self, template_dir: Path, output_dir: Path, config_file: Path, min_delay=5.0):
        super().__init__()
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.config_file = config_file
        self.last_sync = time.time()
        self.min_delay = min_delay
        self.settings: Optional[Dict] = None

    def on_any_event(self, event: FileSystemEvent):
        path = Path(event.src_path)
        if self.is_change_relevant(path):
            logger.debug(f"change detected: {event}")
            now = time.time()
            # don't update too frequently
            if now - self.last_sync > self.min_delay:
                rel_path = path.relative_to(self.template_dir)
                print(f"[green]updating[/green] due to change in '{rel_path}'")
                self.settings = self.read_config()
                self.sync_output()
                self.last_sync = now

    def is_change_relevant(self, path: Path) -> bool:
        if path.name.endswith('~'):
            logger.debug("ignoring temporary files (ending with ~")
            return False
        if self.path_is_relative_to(path, self.output_dir):
            logger.debug("ignoring changes in the output directory")
            return False
        rel_path = path.relative_to(self.template_dir)
        if rel_path.parts[0].startswith('.'):
            logger.debug("ignoring changes to dot-files in the template's root folder")
            return False
        return True

    def read_config(self) -> Optional[Dict]:
        if self.config_file.is_file():
            with self.config_file.open('r') as fp:
                return yaml.load(fp, Loader=FullLoader)
        else:
            logger.warning(f"config file {self.config_file} was not found")

    def sync_output(self):
        with TemporaryDirectory() as temp_dir:
            self.render_template(temp_dir)
            sync(temp_dir, self.output_dir, 'sync', content=True, purge=True,
                 ignore=['.git'], logger=logger)
        logger.debug("file sync complete")

    def render_template(self, output_dir: Union[str, Path]):
        cookiecutter(
            str(self.template_dir),
            extra_context=self.settings,
            no_input=True,
            output_dir=str(output_dir))

    @staticmethod
    def path_is_relative_to(path: Path, other: Path) -> bool:
        try:
            path.relative_to(other)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    app()
