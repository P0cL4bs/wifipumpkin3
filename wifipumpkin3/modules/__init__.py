import os
import pkgutil
import sys
import importlib
import re
from wifipumpkin3.core.utility.printer import display_messages

# https://stackoverflow.com/questions/3365740/how-to-import-all-submodules
def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    parser = re.compile(r"(\s*)wifipumpkin3.modules.(\s*)")
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        short_name = "{}.{}".format(parser.sub("", package.__name__), name)
        results[short_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def all_modules():
    modules = import_submodules(__name__)
    for module in modules:
        try:
            # print(module)
            if not (os.path.isdir(module.replace(".", "/"))):
                current_module = modules[module].ModPump()
        except AttributeError:
            print(
                display_messages(
                    "Module {} not has `ModPump` class!".format(module), error=True
                )
            )


def module_list():
    return import_submodules(__name__)
