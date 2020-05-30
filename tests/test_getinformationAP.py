import unittest
import re


# command : sudo iw dev wlan1 station get 04:b1:67:6e:c0:2a
parser_raw_data = """
Station 04:b1:67:6e:c0:2a (on wlxc83a35cef744)
        inactive time:  2372 ms
        rx bytes:       13547
        rx packets:     158
        tx bytes:       7320
        tx packets:     63
        tx retries:     3
        tx failed:      0
        rx drop misc:   0
        signal:         -59 dBm
        signal avg:     -58 dBm
        tx bitrate:     11.0 MBit/s
        rx bitrate:     1.0 MBit/s
        expected throughput:    6.682Mbps
        authorized:     yes
        authenticated:  yes
        associated:     yes
        preamble:       long
        WMM/WME:        no
        MFP:            no
        TDLS peer:      no
        DTIM period:    2
        beacon interval:100
        connected time: 53 seconds
"""


class TestgetInformationAccessPoint(unittest.TestCase):
    def test_decoded_data(self):
        global parser_raw_data
        p = re.compile(r"\s+(.*):\s+(.*)")

        macaddr = self.getMacAddressFromData(parser_raw_data)
        data = {macaddr: {}}

        all_items = re.findall(p, parser_raw_data)
        for item in all_items:
            data[macaddr][item[0]] = item[1]

        self.assertEqual(self.getResult, data)

    def getMacAddressFromData(self, data):
        p = re.compile(r"([0-9a-f]{2}(?::[0-9a-f]{2}){5})", re.IGNORECASE)
        return re.findall(p, data)[0]

    @property
    def getResult(self):
        result = {
            "04:b1:67:6e:c0:2a": {
                "inactive time": "2372 ms",
                "rx bytes": "13547",
                "rx packets": "158",
                "tx bytes": "7320",
                "tx packets": "63",
                "tx retries": "3",
                "tx failed": "0",
                "rx drop misc": "0",
                "signal": "-59 dBm",
                "signal avg": "-58 dBm",
                "tx bitrate": "11.0 MBit/s",
                "rx bitrate": "1.0 MBit/s",
                "expected throughput": "6.682Mbps",
                "authorized": "yes",
                "authenticated": "yes",
                "associated": "yes",
                "preamble": "long",
                "WMM/WME": "no",
                "MFP": "no",
                "TDLS peer": "no",
                "DTIM period": "2",
                "connected time": "53 seconds",
            }
        }
        # for item in result:
        #     for key, value in result[item].items():
        #         print("    {:<15}	{}".format(key, value))
        return result


if __name__ == "__main__":
    unittest.main()
