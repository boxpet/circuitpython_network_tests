# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import alarm

RESULT_BLOCKS = 5
RESULT_NOT_RUN = 255
SLEEP_DELAY = 5
TEST_PATH = "tests"

RADIO_AUTODETECT = 0
RADIO_NATIVE = 1
RADIO_ESP32SPI = 2
RADIO_WIZNET5K = 3


def get_ipv4_address(radio):
    if hasattr(radio, "ipv4_address"):
        return radio.ipv4_address
    else:
        return radio.pretty_ip(radio.ip_address)


def get_radio_force(value=None):
    if value is None:
        value = alarm.sleep_memory[len(TEST_PATH)]

    if value == RADIO_AUTODETECT:
        return None
    elif value == RADIO_NATIVE:
        return "wifi"
    elif value == RADIO_ESP32SPI:
        return "esp32spi"
    elif value == RADIO_WIZNET5K:
        return "wiznet5k"


def select_radio():
    print("Radio options:")
    print(" [0] Autodetect")
    print(" [1] Native")
    print(" [2] ESP32SPI")
    print(" [3] WIZnet5k")
    while True:
        find_radio = input("Choose a radio [0-3]: ")
        print()

        if find_radio in ["0", "1", "2", "3"]:
            return int(find_radio)

        print("Option not found, try again")
