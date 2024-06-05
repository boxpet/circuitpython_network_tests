# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import time
import unittest

import adafruit_connection_manager
import adafruit_ntp
from connection_helper import get_radio
from helpers import get_radio_force

FORCE_RADIO = os.getenv("NETWORK_TEST_RADIO_FORCE", get_radio_force())


class TestNTP(unittest.TestCase):
    def test_ntp(self):
        radio = get_radio(force=FORCE_RADIO)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        ntp = adafruit_ntp.NTP(pool)
        now_1 = ntp.datetime
        assert now_1.tm_year >= 2024  # noqa: PLR2004 Magic value used in comparison
        time.sleep(3)
        ntp = adafruit_ntp.NTP(pool)
        now_2 = ntp.datetime
        micro_1 = time.mktime(now_1)
        micro_2 = time.mktime(now_2)
        assert 1 < (micro_2 - micro_1) < 5  # noqa: PLR2004 Magic value used in comparison
