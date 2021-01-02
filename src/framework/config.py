from multiprocessing import cpu_count

from dynaconf import Dynaconf

from framework import dirs

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
    yaml_loader="safe_load",
)

settings.PORT = settings.PORT or 8000
settings.WEB_CONCURRENCY = settings.WEB_CONCURRENCY or cpu_count() * 2 + 1
