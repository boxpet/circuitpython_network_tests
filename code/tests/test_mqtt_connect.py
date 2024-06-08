# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os

from network_test_case import NetworkTestCase

from helpers import ValidationMatrix


class TestMQTT(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.MQTT_CONNECTION,
    ]

    def test_mqtt_connect(self):
        from adafruit_minimqtt import adafruit_minimqtt

        aio_username = os.getenv("AIO_USERNAME")
        aio_key = os.getenv("AIO_KEY")

        mqtt_client = adafruit_minimqtt.MQTT(
            broker="io.adafruit.com",
            username=aio_username,
            password=aio_key,
            socket_pool=self.pool,
        )
        mqtt_client.connect()

    def test_mqtt_bad_password(self):
        from adafruit_minimqtt import adafruit_minimqtt

        aio_username = os.getenv("AIO_USERNAME")
        aio_key = "invalid"

        mqtt_client = adafruit_minimqtt.MQTT(
            broker="io.adafruit.com",
            username=aio_username,
            password=aio_key,
            socket_pool=self.pool,
        )
        with self.assertRaises(adafruit_minimqtt.MMQTTException) as exc:
            mqtt_client.connect()
        self.assertIn("Connection Refused - Unauthorized", str(exc.exception_value))
