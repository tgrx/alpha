import sys


def discover_synthetic_venv():
    var_name = "VENV_SYNTHETIC"
    try:
        from dynaconf import settings

        venv = settings.get(var_name)
    except ImportError:
        venv = False

    return venv


def discover_actual_venv():
    compat_prefix = get_base_prefix_compat()
    return compat_prefix != sys.prefix


def get_base_prefix_compat():
    """
    Get base/real prefix, or sys.prefix if there is none.
    """

    prefix = (
        getattr(sys, "base_prefix", None)
        or getattr(sys, "real_prefix", None)
        or sys.prefix
    )

    return prefix


def in_virtualenv():
    synth_venv = discover_synthetic_venv()
    actual_venv = discover_actual_venv()
    return synth_venv or actual_venv


print(in_virtualenv())
