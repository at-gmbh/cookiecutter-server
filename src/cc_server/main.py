import json
import logging
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Optional, Union

import typer
import yaml
from colorama import Fore
from cookiecutter.main import cookiecutter
from dirsync import sync
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
        typer.echo(f"{__title__} {__version__}")
        raise typer.Exit()


TemplatePath = typer.Argument(
    ...,
    help="cookiecutter template source folder (defaults to current folder)",
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
    typer.echo(f"starting {Fore.YELLOW}cookiecutter-server{Fore.RESET} "
               f"(template: '{template}', output: '{output}')")
    server = CookiecutterServer(
        template_dir=template,
        output_dir=output)
    server.serve()


class CookiecutterServer:

    default_config = 'cookiecutter-server.yml'
    template_files = [
        ('cookiecutter.json', json),
        ('cookiecutter.yml', yaml),
        ('cookiecutter.yaml', yaml),
    ]

    def __init__(self, template_dir: Path, output_dir: Path, config_file: Path = None):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.config_file = self._init_config(template_dir, config_file)
        self.observer = Observer()
        self.handler = TemplateUpdate(self.template_dir, self.output_dir, self.config_file)

    def serve(self):
        # render the template for the first time, if the output directory does not exist
        if not self.output_dir.is_dir():
            self.handler.render_template(self.output_dir)
        # start the watchdog
        self.observer.schedule(self.handler, self.template_dir, recursive=True)
        self.observer.start()
        logger.info(f"Cookiecutter Server is watching '{self.template_dir}' for changes")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        typer.echo(f"{Fore.YELLOW}cookiecutter-server{Fore.RESET} terminated")

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
        # ignore temporary files
        if not path.name.endswith('~'):
            logger.debug(f"change detected: {event}")
            now = time.time()
            # don't update too frequently
            if now - self.last_sync > self.min_delay:
                typer.echo(f"{Fore.GREEN}updating{Fore.RESET} due to change in "
                           f"'{path.relative_to(self.template_dir)}'")
                self.settings = self.read_config()
                self.sync_output()
                self.last_sync = now

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


if __name__ == "__main__":
    app()
