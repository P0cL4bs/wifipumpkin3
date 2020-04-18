import unittest
from wifipumpkin3.exceptions.errors.dhcpException import DHCPServerSettingsError
from wifipumpkin3.core.common.platforms import Linux


class TestException(unittest.TestCase):
    def test_dhcp_error_message(self):
        with self.assertRaises(DHCPServerSettingsError):
            raise DHCPServerSettingsError("", "")

    def test_read_file_exception(self):
        self.result_content = "dhcp test massage"
        self.get_file_content = Linux.readFileExceptions("dhcp_test_message")
        self.assertEqual(self.result_content, self.get_file_content)

    # def test_raise(self):
    #     raise DHCPServerSettingsError('DHCP Server', 'range ip error')


if __name__ == "__main__":
    unittest.main()
