#!/usr/bin/env python
# XXX: Makefile.in.mk depends on the position of this file
# XXX: Mac OS X still uses Python 2 as system python, so this code MUST work under Python 2

"""
Exits with 1 when called within active Python virtualenv
"""

import sys


def in_virtualenv():
    try:
        from framework.config import VENV_SYNTHETIC
    except ImportError:
        VENV_SYNTHETIC = False

    synth_venv = VENV_SYNTHETIC
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
