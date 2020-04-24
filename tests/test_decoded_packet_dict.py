from wifipumpkin3.core.common.platforms import decoded
import unittest

result = {
    "IP": {
        "version": 4,
        "src": "10.0.0.21",
        "dst": "216.58.202.227",
        "ihl": 5,
        "tos": 0,
    },
    "Headers": {
        "Connection": "Keep-Alive",
        "Method": "GET",
        "Path": "/generate_204",
        "Http-Version": "HTTP/1.1",
    },
}


class TestConfigPumpkinProxy(unittest.TestCase):
    def test_decoded_data(self):
        global result
        data = {
            "IP": {
                "version": 4,
                "src": "10.0.0.21".encode(),
                "dst": "216.58.202.227".encode(),
                "ihl": 5,
                "tos": 0,
            },
            "Headers": {
                "Connection": "Keep-Alive".encode(),
                "Method": "GET".encode(),
                "Path": "/generate_204".encode(),
                "Http-Version": "HTTP/1.1".encode(),
            },
        }
        # decode byte array to str ascii
        with decoded(data) as data_decoded:
            self.data_decoded = data_decoded

        self.assertEqual(result, self.data_decoded)


if __name__ == "__main__":
    unittest.main()
