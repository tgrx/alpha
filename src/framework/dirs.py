from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_REPO = _this_file.parent.parent.parent.resolve()

DIR_CONFIG = (DIR_REPO / "config").resolve()
DIR_CONFIG_SECRETS = DIR_CONFIG / ".secrets"
DIR_CONFIG_SECRETS.mkdir(exist_ok=True)

DIR_IDEA = (DIR_REPO / ".idea").resolve()

DIR_SRC = (DIR_REPO / "src").resolve()
DIR_FRAMEWORK = (DIR_SRC / "framework").resolve()

DIR_SCRIPTS = (DIR_REPO / "scripts").resolve()

DIR_TESTS = (DIR_REPO / "tests").resolve()

DIR_TEST_ARTIFACTS = (DIR_REPO / ".tests_artifacts").resolve()
DIR_TEST_ARTIFACTS.mkdir(exist_ok=True)
