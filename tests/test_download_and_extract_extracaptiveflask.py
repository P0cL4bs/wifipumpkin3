import unittest
from wifipumpkin3.core.common.platforms import Linux
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI
import tempfile
import requests
import os
from os import path
from zipfile import ZipFile


class TestDownloadCaptiveFlaskTemplates(unittest.TestCase):
    def setUp(self):
        url = "https://github.com/mh4x0f/extra-captiveflask/archive/master.zip"
        save_path = tempfile.gettempdir() + "/master.zip"
        chunk_size = 128
        r = requests.get(url, stream=True)
        with open(save_path, "wb") as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        self.assertTrue(path.isfile(save_path))

    def test_unzip_file(self):
        path_to_zip_file = tempfile.gettempdir() + "/master.zip"
        with ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extractall(tempfile.gettempdir())
        extracted_filepath = tempfile.gettempdir() + "/extra-captiveflask-master"

        self.assertTrue(path.isdir(extracted_filepath))


if __name__ == "__main__":
    unittest.main()
