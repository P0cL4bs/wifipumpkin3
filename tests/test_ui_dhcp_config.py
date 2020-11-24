import unittest
from wifipumpkin3.exceptions.errors.dhcpException import DHCPServerSettingsError
from wifipumpkin3.core.common.platforms import Linux

from wifipumpkin3.core.ui.dhcpConfig import ui_DhcpSettingsClass

class TestUIDHCPSettings(unittest.TestCase):
    def test_dhcp_error_message(self):
        with self.assertRaises(DHCPServerSettingsError):
            raise DHCPServerSettingsError("", "")

    def test_read_file_exception(self):
        pass
        #self.result_content = ui_DhcpSettingsClass(self)
        #self.result_content.start()

    # def test_raise(self):
    #     raise DHCPServerSettingsError('DHCP Server', 'range ip error')


if __name__ == "__main__":
    unittest.main()
