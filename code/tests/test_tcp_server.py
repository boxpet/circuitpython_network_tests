# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import time
from errno import EAGAIN

from network_test_case import NetworkTestCase, SkipTest

from helpers import (
    ValidationMatrix,
    check_time,
    generate_random_number_values,
    get_ipv4_address,
)

PORT = os.getenv("NETWORK_TEST_SERVER_PORT", None) or 5000
MESSAGE_LOOPS = os.getenv("NETWORK_TEST_TCP_MESSAGE_LOOPS", None) or 3
MESSAGE_TIMEOUT = os.getenv("NETWORK_TEST_TCP_MESSAGE_TIMEOUT", None) or 60


class TestTCPServer(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.SERVER_TCP,
    ]

    def test_esp32spi_tcp_server(self):
        if self.radio.__class__.__name__ != "ESP_SPIcontrol":
            raise SkipTest("self.radio isn't an ESP32SPI")

        ip_address = get_ipv4_address(self.radio)
        sock = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_STREAM)
        self.radio.start_server(PORT, sock._socknum, conn_mode=self.radio.TCP_MODE)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for TCP client connection.", end="")

        last_message = start = time.monotonic()
        while True:
            sock_client_num = self.radio.socket_available(sock._socknum)
            sock_client = self.pool.socket()
            sock_client._socknum = sock_client_num
            if sock_client and sock_client._socknum != self.pool.NO_SOCKET_AVAIL:
                break

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        last_message = start = time.monotonic()
        while True:
            bytes_available = sock_client._available()
            if bytes_available:
                print("R", end="")
                data = self.radio.socket_read(sock_client._socknum, bytes_available)
                self.assertEqual(data, b"Hello World!")
                break

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        for i in range(MESSAGE_LOOPS):
            test_data, test_expected = generate_random_number_values()
            print("S", end="")
            sock_client.send(test_data)

            last_message = start = time.monotonic()
            while True:
                bytes_available = sock_client._available()
                if bytes_available:
                    print("R", end="")
                    data = self.radio.socket_read(sock_client._socknum, bytes_available)
                    self.assertEqual(data, test_expected)
                    break

                last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        sock_client.close()
        sock.close()

    def test_native_tcp_server(self):
        if self.radio.__class__.__name__ == "ESP_SPIcontrol":
            raise SkipTest("self.radio isn't native")

        ip_address = get_ipv4_address(self.radio)
        sock = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_STREAM)
        sock.settimeout(None)
        sock.setsockopt(self.pool.SOL_SOCKET, self.pool.SO_REUSEADDR, 1)
        sock.bind((ip_address, PORT))
        sock.listen(10)
        # TODO: setblocking doesn't seem to work on WIZnet5k, no `dots` print
        sock.setblocking(False)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for TCP client connection.", end="")

        last_message = start = time.monotonic()
        buffer = bytearray(64)
        while True:
            try:
                sock_client, client_address = sock.accept()
                sock_client.settimeout(None)
                break
            except OSError as exc:
                if exc.errno != EAGAIN:
                    raise

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        last_message = start = time.monotonic()
        while True:
            bytes_read = sock_client.recv_into(buffer, len(buffer))
            if bytes_read:
                print("R", end="")
                data = bytes(buffer[:bytes_read])
                self.assertEqual(data, b"Hello World!")
                break

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        for i in range(MESSAGE_LOOPS):
            test_data, test_expected = generate_random_number_values()
            print("S", end="")
            sock_client.send(test_data)

            last_message = start = time.monotonic()
            while True:
                bytes_read = sock_client.recv_into(buffer, len(buffer))
                if bytes_read:
                    print("R", end="")
                    data = bytes(buffer[:bytes_read])
                    self.assertEqual(data, test_expected)
                    break

                last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        sock_client.close()
