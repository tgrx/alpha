import pytest

from alpha import dirs

pytestmark = [
    pytest.mark.unit,
]


def test_alpha_dirs() -> None:
    assert dirs.DIR_ALPHA.is_dir()
    assert dirs.DIR_ALPHA.is_relative_to(dirs.DIR_SRC)
    assert dirs.DIR_SRC.is_relative_to(dirs.DIR_REPO)
