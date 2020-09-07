import unittest
from wifipumpkin3.core.common.platforms import Linux
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
import tempfile
import requests
import os
from os import path
from zipfile import ZipFile
import pkgutil
import sys


class TestDownloadCaptiveFlaskTemplates(unittest.TestCase):
    def setUp(self):
        url = "https://github.com/mh4x0f/extra-captiveflask/archive/master.zip"
        save_path = tempfile.gettempdir() + "/master.zip"
        chunk_size = 128
        r = requests.get(url, stream=True)
        with open(save_path, "wb") as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)

        path_to_zip_file = tempfile.gettempdir() + "/master.zip"
        with ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())
        extracted_filepath = tempfile.gettempdir() + "/extra-captiveflask-master"

    def test_read_config_SettingsINI(self):
        config_file_ini = (
            tempfile.gettempdir() + "/extra-captiveflask-master/config.ini"
        )
        config = SettingsINI(config_file_ini)

        result = {
            "example": {
                "author": "mh4x0f",
                "description": "Example is a simple portal default page",
                "preview": "https://i.imgur.com/G0wtAme.png",
                "name": "example",
                "version": "1.0",
            }
        }
        plugins = {}
        for plugin in config.get_all_childname("plugins"):
            plugins[plugin] = {}
            for info in config.get_all_childname("info_{}".format(plugin)):
                plugins[plugin][info] = config.get("info_{}".format(plugin), info)
        for plugin in plugins:
            print(plugin)

        self.assertEqual(result["example"], plugins["example"])

    def test_import_plugins(self):
        pass


if __name__ == "__main__":
    unittest.main()
