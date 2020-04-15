#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from distutils.util import strtobool
import os
import glob
import shutil
import re
from distutils.dir_util import copy_tree


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


folders = ["config", "logs", "helps", "scripts", "exceptions"]


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
    description="Framework for Rogue Wi-Fi Access Point Attack",
    author="Marcos Bomfim (mh4x0f) - P0cL4bs Team",
    author_email="mh4root@gmail.com",
    url="https://github.com/P0cL4bs/wifipumpkin3",
    license="apache 2.0",
    long_description=open("README.md").read(),
    install_requires=required,
    scripts=["bin/wifipumpkin3", "bin/sslstrip3", "bin/captiveflask"],
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache 2.0 License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
)
