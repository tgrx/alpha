# XXX: Makefile.in.mk depends on the position of this file
# XXX: Mac OS X still uses Python 2 as system python, so this code MUST work under Python 2

import sys


def in_virtualenv():
    try:
        from framework.util.settings import get_setting
    except ImportError:
        # noinspection PyUnresolvedReferences
        from settings import get_setting

    synth_venv = get_setting("VENV_SYNTHETIC", False, convert=bool)
    actual_venv = _discover_venv_by_prefix()
    return synth_venv or actual_venv


def _discover_venv_by_prefix():
    compat_prefix = _get_base_prefix_compat()
    return compat_prefix != sys.prefix


def _get_base_prefix_compat():
    prefix = (
        getattr(sys, "base_prefix", None)
        or getattr(sys, "real_prefix", None)
        or sys.prefix
    )

    return prefix


if __name__ == "__main__":
    print(in_virtualenv())
