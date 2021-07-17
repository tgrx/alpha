import abc
from argparse import Namespace
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type

COMMANDS: Dict[str, Type["ManagementCommand"]] = {}


class _ManagementCommandMeta(abc.ABCMeta):
    def __new__(
        mcs, name: str, bases: Tuple, attrs: Dict
    ) -> "_ManagementCommandMeta":
        cls = super().__new__(mcs, name, bases, attrs)
        command_name = attrs.get("name")
        if command_name:
            global COMMANDS
            COMMANDS[command_name] = cls  # type: ignore

        return cls


class ManagementCommand(metaclass=_ManagementCommandMeta):
    arguments: Dict[str, str] = {}
    help: Optional[str] = None
    name: Optional[str] = None
    required: bool = False

    def __init__(self, args: Namespace) -> None:
        self.__args = args

    def option_is_active(self, option: str) -> bool:
        dest = self.dest(option)

        value = bool(vars(self.__args).get(dest))
        return value

    @classmethod
    def dest(cls, argument: str) -> str:
        assert cls.name, "name attr MUST be set"
        name = cls.name.replace("-", "").lower()
        arg = argument.replace("-", "").lower()
        dest = f"{name}__{arg}"
        return dest

    def __call__(self) -> Any:
        raise NotImplementedError
