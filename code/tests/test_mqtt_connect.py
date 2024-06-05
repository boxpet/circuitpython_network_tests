# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import unittest

import adafruit_connection_manager
from adafruit_minimqtt import adafruit_minimqtt
from connection_helper import get_radio
from helpers import get_radio_force

FORCE_RADIO = os.getenv("NETWORK_TEST_RADIO_FORCE", get_radio_force())


class TestMQTT(unittest.TestCase):
    def test_mqtt_connect(self):
        radio = get_radio(force=FORCE_RADIO)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)

        aio_username = os.getenv("AIO_USERNAME")
        aio_key = os.getenv("AIO_KEY")

        mqtt_client = adafruit_minimqtt.MQTT(
            broker="io.adafruit.com",
            username=aio_username,
            password=aio_key,
            socket_pool=pool,
        )
        mqtt_client.connect()
        mqtt_client.disconnect()

    def test_mqtt_connect_bad_password(self):
        radio = get_radio(force=FORCE_RADIO)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)

        aio_username = os.getenv("AIO_USERNAME")
        aio_key = "invalid"

        mqtt_client = adafruit_minimqtt.MQTT(
            broker="io.adafruit.com",
            username=aio_username,
            password=aio_key,
            socket_pool=pool,
        )
        with self.assertRaises(adafruit_minimqtt.MMQTTException) as exc:
            mqtt_client.connect()
        self.assertIn("Connection Refused - Unauthorized", str(exc.exception_value))
