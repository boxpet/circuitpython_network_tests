# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

from network_test_case import NetworkTestCase

from helpers import ValidationMatrix


class TestRequestsHTTPSGet(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.REQUESTS_HTTPS,
    ]

    def test_https_redirect(self):
        import adafruit_requests

        requests = adafruit_requests.Session(self.pool, self.ssl_context)

        test_url = "http://www.adafruit.com/api/quotes.php"
        with requests.get(test_url) as response:
            result = response.text
        self.assertIn("author", result)
