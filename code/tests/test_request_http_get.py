# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

from network_test_case import NetworkTestCase

from helpers import ValidationMatrix


class TestRequestsHTTPGet(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.REQUESTS_HTTP,
    ]

    def test_http_simple(self):
        import adafruit_requests

        requests = adafruit_requests.Session(self.pool)

        test_url = "http://wifitest.adafruit.com/testwifi/index.html"
        with requests.get(test_url) as response:
            result = response.text
        self.assertEqual(
            result,
            "This is a test of Adafruit WiFi!\nIf you can read this, its working :)",
        )
