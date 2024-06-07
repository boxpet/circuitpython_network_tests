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
MESSAGE_LOOPS = os.getenv("NETWORK_TEST_UDP_MESSAGE_LOOPS", None) or 3
MESSAGE_TIMEOUT = os.getenv("NETWORK_TEST_UDP_MESSAGE_TIMEOUT", None) or 60


class TestUDPServer(NetworkTestCase):
    VALIDATES = [
        ValidationMatrix.SERVER_UDP,
    ]

    def test_esp32spi_udp_server(self):
        if self.radio.__class__.__name__ != "ESP_SPIcontrol":
            raise SkipTest("self.radio isn't an ESP32SPI")

        ip_address = get_ipv4_address(self.radio)
        sock = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_DGRAM)
        self.radio.start_server(PORT, sock._socknum, conn_mode=self.radio.UDP_MODE)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for UDP client connection.", end="")

        last_message = start = time.monotonic()
        ip_address_client = None
        while True:
            bytes_available = self.radio.socket_available(sock._socknum)
            if bytes_available:
                print("R", end="")
                data = self.radio.socket_read(sock._socknum, bytes_available)
                self.assertEqual(data, b"Hello World!")
                remote_data = self.radio.get_remote_data(sock._socknum)
                ip_address_client = remote_data["ip_addr"]
                break

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        for i in range(MESSAGE_LOOPS):
            test_data, test_expected = generate_random_number_values()
            print("S", end="")
            self.radio.socket_write(
                sock._socknum, test_data, conn_mode=self.radio.UDP_MODE
            )

            last_message = start = time.monotonic()
            while True:
                bytes_available = self.radio.socket_available(sock._socknum)
                if bytes_available:
                    print("R", end="")
                    data = self.radio.socket_read(sock._socknum, bytes_available)
                    self.assertEqual(data, test_expected)
                    break

                last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        sock.close()

    def test_native_udp_server(self):
        if self.radio.__class__.__name__ == "ESP_SPIcontrol":
            raise SkipTest("self.radio isn't native")

        ip_address = get_ipv4_address(self.radio)
        sock = self.pool.socket(self.pool.AF_INET, self.pool.SOCK_DGRAM)
        sock.setsockopt(self.pool.SOL_SOCKET, self.pool.SO_REUSEADDR, 1)
        sock.bind((ip_address, PORT))
        sock.setblocking(False)

        print(f" Server started at: {ip_address}:{PORT}", end="")
        print(" - waiting for UDP client connection.", end="")

        last_message = start = time.monotonic()
        buffer = bytearray(64)
        client_ip_address = None
        while True:
            try:
                bytes_read, client_ip_address = sock.recvfrom_into(buffer)
                if bytes_read:
                    print("R", end="")
                    data = bytes(buffer[:bytes_read])
                    self.assertEqual(data, b"Hello World!")
                    break
            except OSError as exc:
                if exc.errno != EAGAIN:
                    raise

            last_message = check_time(start, last_message, MESSAGE_TIMEOUT)

        for i in range(MESSAGE_LOOPS):
            test_data, test_expected = generate_random_number_values()
            print("S", end="")
            sock.sendto(test_data, client_ip_address)

            last_message = start = time.monotonic()
            while True:
                try:
                    bytes_read, client_ip_address = sock.recvfrom_into(buffer)
                    if bytes_read:
                        print("R", end="")
                        data = bytes(buffer[:bytes_read])
                        self.assertEqual(data, test_expected)
                        break
                except OSError as exc:
                    if exc.errno != EAGAIN:
                        raise

                last_message = check_time(start, last_message, MESSAGE_TIMEOUT)
