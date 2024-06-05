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
TCP_MESSAGE_TIMEOUT = os.getenv("NETWORK_TEST_TCP_MESSAGE_TIMEOUT", None) or 60


"""
When the TCP server tests are running they will display something like:
-----
test_esp32spi_tcp_server (TestTCPServer) ... skipped: Radio isn't an ESP32SPI
test_native_tcp_server (TestTCPServer) ... Server started at: 192.168.xx.xx:5000 - waiting for TCP client message.....
-----
Once you see "waiting for TCP client message", it will add a "." every second until it get's a message.
To send a message, paste this method into a CPython terminal and call it with the IP and port from the test
"""


def tcp_client_send(ip=None, port=None):
    import socket

    if ip is None:
        ip = input("IP? ")
    if port is None:
        port = input("Port? ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect((ip, port))
        size = sock.send(b"Hello World!")
        print(f"Sent {size} bytes to {ip}:{port}")


class TestTCPServer(unittest.TestCase):
    def test_esp32spi_tcp_server(self):
        radio = get_radio(force=FORCE_RADIO)
        if radio.__class__.__name__ != "ESP_SPIcontrol":
            raise unittest.SkipTest("Radio isn't an ESP32SPI")

        ip_address = get_ipv4_address(radio)
        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        radio.start_server(PORT, sock._socknum, conn_mode=radio.TCP_MODE)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for TCP client message", end="")

        last_message = start = time.monotonic()
        while True:
            sock_client_num = radio.socket_available(sock._socknum)
            sock_client = pool.socket()
            sock_client._socknum = sock_client_num
            if sock_client and sock_client._socknum != pool.NO_SOCKET_AVAIL:
                bytes_available = sock_client._available()
                data = radio.socket_read(sock_client._socknum, bytes_available)
                self.assertEqual(data, b"Hello World!")
                break

            elasped = time.monotonic()
            if int(elasped - last_message) >= 1:
                last_message = elasped
                print(".", end="")

            if int(elasped - start) > TCP_MESSAGE_TIMEOUT:
                raise TimeoutError(
                    f"Didn't recieve TCP message within {TCP_MESSAGE_TIMEOUT} seconds"
                )

    def test_native_tcp_server(self):
        radio = get_radio(force=FORCE_RADIO)
        if radio.__class__.__name__ == "ESP_SPIcontrol":
            raise unittest.SkipTest("Radio isn't native")

        ip_address = get_ipv4_address(radio)
        if radio.__class__.__name__ == "Radio":
            ip_address_server = "0.0.0.0"
        else:
            ip_address_server = ip_address

        pool = adafruit_connection_manager.get_radio_socketpool(radio)
        sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        sock.settimeout(None)
        sock.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
        sock.bind((ip_address_server, PORT))
        sock.listen(10)
        # TODO: setblocking doesn't seem to work on WIZnet5k, no `dots` print
        sock.setblocking(False)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for TCP client message", end="")

        last_message = start = time.monotonic()
        buffer = bytearray(64)
        while True:
            try:
                connection, client_address = sock.accept()
                connection.settimeout(None)
                bytes_read = connection.recv_into(buffer, len(buffer))
                if bytes_read:
                    data = bytes(buffer[:bytes_read])
                    self.assertEqual(data, b"Hello World!")
                    connection.close()
                    break
                connection.close()
            except OSError as exc:
                if exc.errno != EAGAIN:
                    raise

            elasped = time.monotonic()
            if int(elasped - last_message) >= 1:
                last_message = elasped
                print(".", end="")

            if int(elasped - start) > TCP_MESSAGE_TIMEOUT:
                raise TimeoutError(
                    f"Didn't recieve TCP message within {TCP_MESSAGE_TIMEOUT} seconds"
                )
