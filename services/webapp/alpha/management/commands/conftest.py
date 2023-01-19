import importlib.util
import shutil
import sys
from pathlib import Path
from types import ModuleType
from typing import Generator
from uuid import uuid4

import pytest

from alpha import dirs


@pytest.fixture
def cloned_repo(tmp_path: Path) -> Generator[Path, None, None]:
    repo_id = str(uuid4())
    repo = (tmp_path / repo_id).resolve()

    shutil.rmtree(repo, ignore_errors=True)

    shutil.copytree(
        dirs.DIR_REPO,
        repo,
        copy_function=shutil.copy,
        ignore=ignore_on_copy,
    )

    yield repo


@pytest.fixture
def cloned_repo_dirs(cloned_repo: Path) -> Generator[ModuleType, None, None]:
    py_file = (cloned_repo / "src" / "alpha" / "dirs.py").resolve()
    assert py_file.is_file()

    module_name = "alpha.dirs2"

    spec = importlib.util.spec_from_file_location(module_name, py_file)
    assert spec
    assert spec.loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    yield module


def ignore_on_copy(src: str, names: list[str]) -> list[str]:
    assert src

    names_set = set(names)

    ignored_always = {
        ".idea",
        ".local",
        ".venv",
        ".vscode",
        "__pycache__",
    }

    py_compiled = {
        name
        for name in names
        if any(
            name.endswith(ext)
            for ext in {
                ".pyc",
                ".pyi",
                ".pyo",
            }
        )
    }

    ignored = names_set & (ignored_always | py_compiled)

    return sorted(ignored)
