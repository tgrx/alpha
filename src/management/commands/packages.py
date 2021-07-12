import os
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from pathlib import PurePath
from typing import Dict

import toml

from framework.dirs import DIR_REPO
from management.commands.abstract import ManagementCommand

PACKAGES_SECTIONS = {"packages", "dev-packages"}
PIPFILE = (DIR_REPO / "Pipfile").resolve()
assert PIPFILE.is_file, f"can not open {PIPFILE.as_posix()} to read"


class UpgradePackagesCommand(ManagementCommand):
    name = "upgrade-packages"

    def __call__(self):
        backup = backup_pipfile()
        try:
            original = load_pipfile()
            relaxed = relax_packages_versions(original)
            save_pipfile(relaxed)
            upgrade_packages()
            installed_packages = get_installed_packages()
            fixed = fix_packages_versions(relaxed, installed_packages)
            save_pipfile(fixed)
            upgrade_packages()
        except:
            restore_pipfile_from_backup(backup)
            raise


def backup_pipfile() -> Path:
    suffix = datetime.utcnow().strftime(".%Y-%m-%d-%H-%M-%S-%f.bak")
    backup = PIPFILE.with_suffix(suffix)
    shutil.copyfile(PIPFILE, backup)
    return backup


def restore_pipfile_from_backup(backup: PurePath) -> None:
    shutil.copyfile(backup, PIPFILE)
    os.unlink(backup)


def relax_packages_versions(pipfile: Dict) -> Dict:
    def version_func(_pkg_name, _pkg_params):
        if isinstance(_pkg_params, str) and "b" not in _pkg_params:
            return "*"
        if isinstance(_pkg_params, dict) and "version" in _pkg_params:
            return version_func(_pkg_name, _pkg_params["version"])
        return _pkg_params

    pipfile_new = _set_packages_versions(pipfile, version_func)
    return pipfile_new


def fix_packages_versions(pipfile: Dict, installed_packages: Dict) -> Dict:
    def version_func(_pkg_name, _pkg_params):
        version = installed_packages[_pkg_name.lower()]
        return f"=={version}"

    pipfile_new = _set_packages_versions(pipfile, version_func)
    return pipfile_new


def get_installed_packages() -> Dict:
    cmd = "pip freeze"
    args = shlex.split(cmd)
    run = subprocess.run(args, check=True, capture_output=True)
    output = run.stdout.decode()
    packages = {
        package_name.lower(): version
        for package_name, version in [
            package.split("==") for package in output.split("\n") if package
        ]
    }
    return packages


def upgrade_packages() -> None:
    cmd = "pipenv update --dev"
    args = shlex.split(cmd)
    subprocess.run(
        args,
        check=True,
        env={
            "PATH": os.getenv("PATH"),
        },
    )


def load_pipfile() -> Dict:
    with PIPFILE.open("r") as src:
        content = toml.load(src)
    return content


def save_pipfile(pipfile: Dict) -> None:
    with PIPFILE.open("w") as dst:
        toml.dump(pipfile, dst)


def _set_packages_versions(pipfile: Dict, version_func) -> Dict:
    versioned = {}

    # to keep "packages*" sections in the end of Pipfile
    sorted_sections = sorted(
        pipfile.items(), key=lambda _s: (_s[0] in PACKAGES_SECTIONS, _s)
    )

    for section_name, section in sorted_sections:
        if section_name not in PACKAGES_SECTIONS:
            versioned[section_name] = section
            continue

        packages = versioned.setdefault(section_name, {})

        for package_name, package_params in sorted(section.items()):
            version = version_func(package_name, package_params)
            if isinstance(package_params, str):
                packages[package_name] = version
            elif (
                isinstance(package_params, dict)
                and "version" in package_params
            ):
                packages[package_name] = {**package_params, "version": version}
            else:
                packages[package_name] = package_params

    return versioned
