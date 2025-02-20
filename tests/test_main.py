import shutil
import time
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from typer.testing import CliRunner

from cookiecutter_server.main import CookiecutterServer, app
from tests import test_template_dir

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_no_args():
    result = runner.invoke(app, [])
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout


def test_serve():
    with TemporaryDirectory() as tmp_dir, StringIO() as buf, redirect_stdout(buf):
        # copy the template to a temporary directory
        tmp_dir = Path(tmp_dir)
        tmp_template = tmp_dir / 'template'
        tmp_serve = tmp_dir / 'serve'
        shutil.copytree(test_template_dir, tmp_template)

        # start the server in a separate thread
        cc_server = CcServerThread(template_dir=tmp_template, output_dir=tmp_serve)
        cc_server.start()

        # wait until the template is rendered
        while "template is ready" not in buf.getvalue():
            time.sleep(0.01)

        # check that all files are in place
        server_yml = tmp_template / 'cookiecutter-server.yml'
        readme_template = tmp_template / '{{cookiecutter.project_slug}}/README.md'
        readme_serve = tmp_serve / 'my-project/README.md'
        assert server_yml.exists()
        assert readme_template.exists()
        assert readme_serve.exists()

        # now modify the template
        with readme_template.open('a') as fp:
            fp.write("\nyolo!\n")

        # wait until the modification is found in the served file
        for _ in range(10):
            if 'yolo!' not in readme_serve.read_text():
                time.sleep(0.1)
        assert 'yolo!' in readme_serve.read_text()

        # gracefully shut down the server
        cc_server.stop()


class CcServerThread(Thread):

    def __init__(self, template_dir: Path, output_dir: Path):
        super().__init__(daemon=True)
        self.server = CookiecutterServer(
            template_dir=template_dir, output_dir=output_dir, min_delay=0)

    def run(self):
        self.server.serve()

    def stop(self):
        self.server.signal_stop = True
        self.join(timeout=0.5)
