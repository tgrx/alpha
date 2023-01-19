from pathlib import Path

_this_file = Path(__file__)
_resolved = False

DIR_ALPHA = _this_file.parent

DIR_APP = DIR_ALPHA.parent

DIR_SERVICES = DIR_APP.parent

DIR_REPO = DIR_SERVICES.parent

DIR_SCRIPTS = DIR_APP / "scripts"


def _resolve() -> None:
    global _resolved
    if _resolved:
        return

    import sys
    from functools import partial

    this_module = sys.modules[__name__]

    names = dir(this_module)
    _getattr = partial(getattr, this_module)
    namespace = zip(names, map(_getattr, names))
    paths = filter(lambda _pair: isinstance(_pair[1], Path), namespace)

    for name, obj in paths:
        obj = obj.resolve()
        setattr(this_module, name, obj)

    _resolved = True


_resolve()

__all__ = (
    "DIR_ALPHA",
    "DIR_APP",
    "DIR_REPO",
    "DIR_SCRIPTS",
    "DIR_SERVICES",
)
