# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import time
import unittest
from errno import EAGAIN

import adafruit_connection_manager
from connection_helper import get_radio
from helpers import get_ipv4_address, get_radio_force

FORCE_RADIO = os.getenv("NETWORK_TEST_RADIO_FORCE", get_radio_force())
PORT = os.getenv("NETWORK_TEST_SERVER_PORT", None) or 5000
UDP_MESSAGE_TIMEOUT = os.getenv("NETWORK_TEST_UDP_MESSAGE_TIMEOUT", None) or 60


"""
When the UDP server tests are running they will display something like:
-----
test_esp32spi_udp_server (TestUDPServer) ... skipped: Radio isn't an ESP32SPI
test_native_udp_server (TestUDPServer) ... Server started at: 192.168.xx.xx:5000 - waiting for UDP client message.....
-----
Once you see "waiting for UDP client message", it will add a "." every second until it get's a message.
To send a message, paste this method into a CPython terminal and call it with the IP and port from the test
"""


def utp_client_send(ip=None, port=None):
    import socket

    if ip is None:
        ip = input("IP? ")
    if port is None:
        port = input("Port? ")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        size = sock.sendto(b"Hello World!", (ip, port))
        print(f"Sent {size} bytes to {ip}:{port}")


class TestUDPServer(unittest.TestCase):
    def test_esp32spi_udp_server(self):
        radio = get_radio(force=FORCE_RADIO)
        if radio.__class__.__name__ != "ESP_SPIcontrol":
            raise unittest.SkipTest("Radio isn't an ESP32SPI")

        ip_address = get_ipv4_address(radio)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
        radio.start_server(PORT, sock._socknum, conn_mode=radio.UDP_MODE)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for UDP client message", end="")

        last_message = start = time.monotonic()
        while True:
            bytes_available = radio.socket_available(sock._socknum)
            if bytes_available:
                data = radio.socket_read(sock._socknum, bytes_available)
                self.assertEqual(data, b"Hello World!")
                break

            elasped = time.monotonic()
            if int(elasped - last_message) >= 1:
                last_message = elasped
                print(".", end="")

            if int(elasped - start) > UDP_MESSAGE_TIMEOUT:
                raise TimeoutError(
                    f"Didn't recieve UDP message within {UDP_MESSAGE_TIMEOUT} seconds"
                )

    def test_native_udp_server(self):
        radio = get_radio(force=FORCE_RADIO)
        if radio.__class__.__name__ == "ESP_SPIcontrol":
            raise unittest.SkipTest("Radio isn't native")

        ip_address = get_ipv4_address(radio)
        if radio.__class__.__name__ == "Radio":
            ip_address_server = "0.0.0.0"
        else:
            ip_address_server = ip_address

        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
        sock.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
        sock.bind((ip_address_server, PORT))
        sock.setblocking(False)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for UDP client message", end="")

        last_message = start = time.monotonic()
        buffer = bytearray(64)
        while True:
            try:
                bytes_read = sock.recv_into(buffer, len(buffer))
                if bytes_read:
                    data = bytes(buffer[:bytes_read])
                    self.assertEqual(data, b"Hello World!")
                    break
            except OSError as exc:
                if exc.errno != EAGAIN:
                    raise

            elasped = time.monotonic()
            if int(elasped - last_message) >= 1:
                last_message = elasped
                print(".", end="")

            if int(elasped - start) > UDP_MESSAGE_TIMEOUT:
                raise TimeoutError(
                    f"Didn't recieve UDP message within {UDP_MESSAGE_TIMEOUT} seconds"
                )
