import abc
from typing import Dict
from typing import Optional

COMMANDS = {}


class _ManagementCommandMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        name = attrs.get("name")
        if name:
            global COMMANDS
            COMMANDS[name] = cls

        return cls


class ManagementCommand(metaclass=_ManagementCommandMeta):
    arguments: Dict[str, str] = {}
    help: Optional[str] = None
    name: Optional[str] = None
    required: bool = False

    def __init__(self, args):
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
