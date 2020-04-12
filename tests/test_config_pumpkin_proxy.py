import unittest
from wifipumpkin3.core.common.platforms import Linux
import wifipumpkin3.core.utility.constants as C
from wifipumpkin3.core.utility.collection import SettingsINI


class TestConfigPumpkinProxy(unittest.TestCase):
    def test_config_key_set(self):
        self.config = SettingsINI(C.CONFIG_PP_INI)
        self.result = "http://example.com/foo.js"
        self.value = self.config.get("set_js_inject", "url")
        self.assertEqual(self.result, self.value)

    def test_get_all_configkey_list(self):
        self.config = SettingsINI(C.CONFIG_PP_INI)
        self.result = ["url"]
        self.value = self.config.get_all_childname("set_js_inject")
        self.assertEqual(self.result, self.value)


if __name__ == "__main__":
    unittest.main()
