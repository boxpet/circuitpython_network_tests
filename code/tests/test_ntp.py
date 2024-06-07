# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import time

from network_test_case import NetworkTestCase

from helpers import ValidationMatrix


class TestNTP(NetworkTestCase):
    VALIDATES = [ValidationMatrix.REQUESTS_NTP, ValidationMatrix.REQUESTS_UDP]

    def test_ntp(self):
        import adafruit_ntp

        ntp = adafruit_ntp.NTP(self.pool)
        now_1 = ntp.datetime
        assert now_1.tm_year >= 2024  # noqa: PLR2004 Magic value used in comparison
        time.sleep(3)
        ntp = adafruit_ntp.NTP(self.pool)
        now_2 = ntp.datetime
        micro_1 = time.mktime(now_1)
        micro_2 = time.mktime(now_2)
        assert 1 < (micro_2 - micro_1) < 5  # noqa: PLR2004 Magic value used in comparison
