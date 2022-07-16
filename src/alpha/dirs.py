import os
from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_ALPHA = _this_file.parent.resolve()

DIR_SRC = DIR_ALPHA.parent.resolve()

DIR_REPO = DIR_SRC.parent.resolve()

DIR_CONFIG = (DIR_REPO / "config").resolve()
DIR_CONFIG_SECRETS = Path(os.getenv("SECRETS_DIR", DIR_CONFIG / ".secrets"))
DIR_CONFIG_SECRETS.mkdir(exist_ok=True)

DIR_DOCS = (DIR_REPO / "docs").resolve()

DIR_SCRIPTS = (DIR_REPO / "scripts").resolve()

DIR_TESTS = (DIR_REPO / "tests").resolve()

DIR_CI = (DIR_REPO / ".github").resolve()
DIR_CI_WORKFLOWS = (DIR_CI / "workflows").resolve()

DIR_RUN_CONFIGURATIONS = (DIR_REPO / ".run").resolve()
