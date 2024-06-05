# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import unittest

import adafruit_connection_manager
import adafruit_requests
from connection_helper import get_radio
from helpers import get_radio_force

FORCE_RADIO = os.getenv("NETWORK_TEST_RADIO_FORCE", get_radio_force())


class TestRequestsGet(unittest.TestCase):
    def test_http_simple(self):
        radio = get_radio(force=FORCE_RADIO)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        requests = adafruit_requests.Session(pool)

        test_url = "http://wifitest.adafruit.com/testwifi/index.html"
        with requests.get(test_url) as response:
            result = response.text
        self.assertEqual(
            result,
            "This is a test of Adafruit WiFi!\nIf you can read this, its working :)",
        )

    def test_https_redirect(self):
        radio = get_radio(force=FORCE_RADIO)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(radio)
        requests = adafruit_requests.Session(pool, ssl_context)

        test_url = "https://www.adafruit.com/api/quotes.php"
        with requests.get(test_url) as response:
            result = response.text
        self.assertIn("author", result)
