"""Guard source-upload permissions; an actual Docker smoke test is still required."""
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess

import pytest


@pytest.mark.skipif(os.name != 'posix', reason='The container uses POSIX permissions')
def test_runtime_sources_are_readable_after_restrictive_upload(tmp_path):
    backend = Path(__file__).resolve().parents[1]
    dockerfile = (backend / 'Dockerfile').read_text()
    command = re.search(r'chmod -R ([a-zA-Z,+-]+) /app', dockerfile)
    assert command, 'Normalize copied source permissions before switching to appuser'
    assert dockerfile.index('COPY data ./data') < command.start() < dockerfile.index('USER appuser')

    image = tmp_path / 'app'
    image.mkdir()
    for name in ('main.py', 'requirements.txt', 'app', 'phishhook', 'data'):
        source = backend / name
        if source.is_dir():
            shutil.copytree(source, image / name, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            shutil.copy2(source, image / name)
    paths = [image, *image.rglob('*')]
    # A clean git clone under umask 077 has these modes. Docker COPY leaves
    # these files root-owned, so the default non-root user needs other access.
    for path in paths:
        path.chmod(0o700 if path.is_dir() else 0o600)
    subprocess.run(['chmod', '-R', command[1], str(image)], check=True)
    for path in paths:
        mode = path.stat().st_mode
        assert mode & stat.S_IROTH, f'Runtime user cannot read {path.relative_to(image)}'
        if path.is_dir():
            assert mode & stat.S_IXOTH, f'Runtime user cannot traverse {path.relative_to(image)}'
        else:
            assert not mode & stat.S_IXOTH, 'Ordinary source files need no execute bit'
        assert not mode & (stat.S_IWGRP | stat.S_IWOTH), 'Do not add group/other write access'
