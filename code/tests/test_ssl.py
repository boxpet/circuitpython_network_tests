# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

from network_test_case import NetworkTestCase

from helpers import ValidationMatrix


class TestNativeSSL(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.CORE_SSL,
    ]

    def tearDown(self):
        pass

    def test_can_use_ssl(self):
        import ssl

        import adafruit_requests

        ssl_context = ssl.create_default_context()
        requests = adafruit_requests.Session(self.pool, ssl_context)

        test_url = "https://www.adafruit.com/api/quotes.php"
        with requests.get(test_url) as response:
            result = response.text
        self.assertIn("author", result)
