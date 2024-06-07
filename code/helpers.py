# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import random
import time

import alarm

RESULT_BLOCKS = 5
RESULT_NOT_RUN = 255
SLEEP_DELAY = 5
TEST_PATH = "tests"

RADIO_NATIVE = 1
RADIO_ESP32SPI = 2
RADIO_WIZNET5K = 3


class ValidationMatrix:
    MQTT_CONNECTION = "mqtt_connection"
    REQUESTS_HTTP = "requests_http"
    REQUESTS_HTTPS = "requests_https"
    REQUESTS_NTP = "requests_ntp"
    REQUESTS_UDP = "requests_udp"
    SERVER_TCP = "server_tcp"
    SERVER_UDP = "server_upd"

    TEST_RESULTS = {
        "U": "Unknown",
        "N": "No",
        "Y": "Yes",
        "S": "Skipped",
    }

    @classmethod
    def get_all_validations(cls):
        validations = []
        for attribute_name in dir(cls):
            if attribute_name.startswith("__"):
                continue
            attribute = getattr(cls, attribute_name, None)
            if isinstance(attribute, str):
                validations.append(attribute)
        return validations


def check_time(start, last_message, timeout):
    elasped = time.monotonic()

    if int(elasped - start) > timeout:
        raise TimeoutError(f"Didn't recieve message within {timeout} seconds")

    if int(elasped - last_message) >= 1:
        print(".", end="")
        return elasped

    return last_message


def generate_random_number_values(value_min=1, value_max=9):
    test_value = random.randint(value_min, value_max)
    test_expected = str(test_value * 2).encode()
    test_data = str(test_value).encode()
    return test_data, test_expected


def get_ipv4_address(radio):
    if hasattr(radio, "ipv4_address"):
        return str(radio.ipv4_address)
    else:
        return radio.pretty_ip(radio.ip_address)


def get_radio_force(value=None):
    if value is None:
        value = alarm.sleep_memory[len(TEST_PATH)]

    if value == RADIO_NATIVE:
        return "wifi"
    elif value == RADIO_ESP32SPI:
        return "esp32spi"
    elif value == RADIO_WIZNET5K:
        return "wiznet5k"


def select_radio():
    while True:
        print("Radio options:")
        print(" [1] Native")
        print(" [2] ESP32SPI")
        print(" [3] WIZnet5k")

        find_radio = input("Choose a radio [1-3]: ")
        print()

        if find_radio in ["1", "2", "3"]:
            return int(find_radio)

        print("Option not found, try again")
