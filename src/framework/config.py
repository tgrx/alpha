from multiprocessing import cpu_count

from dynaconf import Dynaconf
from dynaconf import Validator

from framework import dirs

_validators = [
    Validator("WEB_CONCURRENCY", default=cpu_count() * 2 + 1)
]

settings = Dynaconf(
    core_loaders=["YAML"],
    env_switcher="ALPHA_ENV",
    environments=True,
    envvar_prefix=False,
    fresh_vars=["DATABASE_URL"],
    ignore_unknown_envvars=True,
    load_dotenv=True,
    root_path=dirs.DIR_CONFIG.as_posix(),
    settings_files=["settings.yml", ".secrets.yml"],
    validators=_validators,
    yaml_loader="safe_load",
)
