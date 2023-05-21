# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import re
from distutils.dir_util import copy_tree
import sys
from itertools import chain

# check version the python install
if not (sys.version_info.major == 3 and sys.version_info.minor >= 7):
    print("[!] Wifipumpkin3 requires Python 3.7 or higher!")
    print(
        "[*] You are using Python {}.{}.".format(
            sys.version_info.major, sys.version_info.minor
        )
    )
    sys.exit(1)


def version(version_file):
    with open(version_file, "r") as f:
        version_file_content = f.read()

    version_match = re.search(
        r"__version__\s*=\s*[\"\']([^\"\']+)", version_file_content
    )
    if version_match:
        return version_match.groups()[0]

    return None


with open("requirements.txt") as fp:
    required = [line.strip() for line in fp if line.strip() != ""]


folders = ["config"]

def generate_data_files():
    data_files = []
    data_dirs = ('config', 'exceptions','helps', 'scripts')
    for path, dirs, files in chain.from_iterable(os.walk(data_dir) for data_dir in data_dirs):
        install_dir = os.path.join('wifipumpkin3/data/' + path)    
        list_entry = (install_dir, [os.path.join(path, f) for f in files if not f.startswith('.')])
        data_files.append(list_entry)

    return data_files

def create_user_dir_config():
    user_config_dir = os.path.expanduser("~") + "/.config/wifipumpkin3"
    if not os.path.isdir(user_config_dir):
        os.makedirs(user_config_dir, exist_ok=True)
    # force copy all files `config` to user_config_dir
    for folder in folders:
        copy_tree(folder, user_config_dir + "/{}".format(folder))


# create dir config
create_user_dir_config()

VERSION_FILE = "wifipumpkin3/_version.py"
wifipumpkin3_version = version(VERSION_FILE)

setup(
    name="wifipumpkin3",
    version=wifipumpkin3_version,
    description="Powerful framework for rogue access point attack.",
    author="Marcos Bomfim (mh4x0f) - P0cL4bs Team",
    author_email="mh4root@gmail.com",
    url="https://github.com/P0cL4bs/wifipumpkin3",
    license="apache 2.0",
    long_description=open("README.md").read(),
    install_requires=required,
    data_files=generate_data_files(),
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    entry_points={
        "console_scripts": [
            "wifipumpkin3=wifipumpkin3.__main__:main",
            "wp3=wifipumpkin3.__main__:main",
            "captiveflask=wifipumpkin3.plugins.bin.captiveflask:main",
            "sslstrip3=wifipumpkin3.plugins.bin.sslstrip3:main",
        ],
    },
)
