import logging
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import typer
from cookiecutter.main import cookiecutter
from dirsync import sync
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from cc_server import __title__, __version__

logging.basicConfig(format="%(asctime)s.%(msecs)03d [%(levelname)s]: %(message)s",
                    level=logging.DEBUG)
logger = logging.getLogger('cc_server')


app = typer.Typer(
    name='cc_server',
    help="A local development server to get live previews of cookiecutter templates")


def version_callback(version: bool):
    if version:
        typer.echo(f"{__title__} {__version__}")
        raise typer.Exit()


TemplatePath = typer.Argument(
    '.',
    help="cookiecutter template source folder (defaults to current folder)")
OutputPath = typer.Option(
    './serve/', '-o', '--output',
    help="output folder (defaults to folder 'serve' under the current folder)")
Version = typer.Option(
    None, '-v', '--version', callback=version_callback, is_eager=True,
    help="print the program version and exit")


@app.command()
def main(template: str = TemplatePath, output: str = OutputPath, version: bool = Version):
    """
    A local development server to get live previews of cookiecutter templates
    """
    logger.info("Looks like you're all set up. Let's get going!")


def serve(template: Path, output: Path):
    settings = {
        'package_manager': 'pip',
        'use_docker': 'yes',
    }
    project_dir = cookiecutter(
        str(template), extra_context=settings, no_input=True, output_dir=str(output))
    w = Watcher(template, MyHandler(template, settings, output))
    w.run()
    pass


class Watcher:

    def __init__(self, directory=".", handler: FileSystemEventHandler = None):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        logger.info(f"Watcher Running in {self.directory}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        logger.info("Watcher Terminated")


class MyHandler(FileSystemEventHandler):

    def __init__(self, template, settings, output):
        super().__init__()
        self.template = template
        self.settings = settings
        self.output = output
        self.last_sync = time.time()

    def on_any_event(self, event: FileSystemEvent):
        path = Path(event.src_path)
        logger.info(f"change detected: {event}")
        if path.name.endswith('~'):
            return  # ignore temporary files
        now = time.time()
        if now - self.last_sync > 5.0:
            logger.info(f"updating due to change in {path.relative_to(self.template)}")
            self.sync_output()
            self.last_sync = now

    def sync_output(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = cookiecutter(
                str(self.template),
                extra_context=self.settings,
                no_input=True,
                output_dir=temp_dir)
            sync(temp_dir, self.output, 'sync')
            pass


if __name__ == "__main__":
    app()
