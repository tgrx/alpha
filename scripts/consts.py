from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_REPO = _this_file.parent.parent.resolve()

DIR_IDEA = (DIR_REPO / ".idea").resolve()
DIR_SCRIPTS = (DIR_REPO / "scripts").resolve()
DIR_SRC = (DIR_REPO / "src").resolve()
