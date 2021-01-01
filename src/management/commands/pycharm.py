import dataclasses
from itertools import chain
from pathlib import Path
from typing import Dict
from typing import Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from dynaconf import settings

from framework.dirs import DIR_IDEA
from management.commands.abstract import ManagementCommand

assert (
    DIR_IDEA.is_dir()
), f"unable to set up PyCharm: config dir `{DIR_IDEA.as_posix()}` not found"


@dataclasses.dataclass
class FolderT:
    folder: str

    tag = "sourceFolder"
    attrs = {}

    @property
    def url(self):
        return f"file://$MODULE_DIR$/{self.folder}"

    @property
    def xml(self):
        attrs = {"url": self.url, **self.attrs}
        return Element(self.tag, attrib=attrs)


class SourcesFolder(FolderT):
    attrs = {"isTestSource": "false"}


class ResourcesFolder(FolderT):
    attrs = {"type": "java-resource"}


class ExcludedFolder(FolderT):
    tag = "excludeFolder"


class TemplateFolder(FolderT):
    tag = "option"

    @property
    def xml(self):
        url = self.url.replace("file://", "")
        attrs = {"value": url}
        return Element(self.tag, attrib=attrs)


PROJECT_FOLDERS = list(
    chain(
        (ExcludedFolder(_f) for _f in settings.DIRS_EXCLUDED),
        (ResourcesFolder(_f) for _f in settings.DIRS_RESOURCES),
        (SourcesFolder(_f) for _f in settings.DIRS_SOURCES),
        (TemplateFolder(_f) for _f in settings.DIRS_TEMPLATES),
    )
)


class SetupPycharmCommand(ManagementCommand):
    name = "setup-pycharm"

    def __call__(self):
        assert (
            settings.PROJECT_NAME
        ), "project name is not configured - look through config/"
        iml = DIR_IDEA / f"{settings.PROJECT_NAME}.iml"
        tree = build_tree(iml)
        root = get_root(tree)
        setup_new_module_root_manager(root)
        setup_template_service(root)
        save_tree(tree, iml)


def build_tree(path: Path) -> ElementTree:
    path = path.resolve()
    posix_path = path.as_posix()
    if not path.is_file():
        raise RuntimeError(f"unable to read XML from {posix_path}")

    tree = ElementTree.parse(posix_path)
    return tree


def get_root(tree: ElementTree) -> Element:
    root = tree.getroot()

    root_tag = "module"
    assert (
        root.tag == root_tag
    ), f"unsupported IML file: malformed structure: root tag != <{root_tag}>"

    return root


def setup_new_module_root_manager(root: Element) -> None:
    component = get_component(root, "NewModuleRootManager", must_exist=True)
    content = get_or_create_tag(
        component,
        "content",
        attrs={"url": "file://$MODULE_DIR$"},
        clear=True,
    )

    for folder in PROJECT_FOLDERS:
        if isinstance(folder, TemplateFolder):
            continue
        content.append(folder.xml)


def setup_template_service(root: Element) -> None:
    component = get_component(root, "TemplatesService", must_exist=False)

    if component is None:
        return
    option_template_config = get_or_create_tag(
        component,
        "option",
        attrs={"name": "TEMPLATE_CONFIGURATION"},
        clear=True,
    )
    option_template_config.set("value", settings.TEMPLATE_ENGINE)

    option_folders = get_or_create_tag(
        component,
        "option",
        attrs={"name": "TEMPLATE_FOLDERS"},
        clear=True,
    )
    folders_list = get_or_create_tag(option_folders, "list", clear=True)

    for folder in PROJECT_FOLDERS:
        if not isinstance(folder, TemplateFolder):
            continue
        folders_list.append(folder.xml)


def save_tree(tree: ElementTree, destination: Path) -> None:
    tree.write(destination, encoding="unicode", xml_declaration=True)


def get_component(
    root: Element, component_name: str, must_exist: bool
) -> Optional[Element]:
    component = root.find(f"./component[@name='{component_name}']")

    if component is None and must_exist:
        errmsg = f"no <component name='{component_name}'> found in XML tree"
        raise RuntimeError(errmsg)
    else:
        return component


def get_or_create_tag(
    parent: Element,
    tag_name: str,
    attrs: Optional[Dict] = None,
    clear: bool = False,
) -> Element:
    attrs = attrs or {}
    xpath_attrs = []
    for attr, value in attrs.items():
        xpath_attrs.append(f"@{attr}='{value}'")
    if xpath_attrs:
        xpath_attrs = " and ".join(xpath_attrs)
        xpath_attrs = f"[{xpath_attrs}]"
    else:
        xpath_attrs = ""

    xpath = f"./{tag_name}{xpath_attrs}"

    tag = parent.find(xpath)
    if tag is None:
        tag = Element(tag_name, attrib=attrs)
        parent.append(tag)

    if clear:
        tag.clear()
        for attr, value in attrs.items():
            tag.set(attr, value)

    return tag


if __name__ == "__main__":
    main()
