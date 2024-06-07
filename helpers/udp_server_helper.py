# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import socket
import time

"""
When the UDP server tests are running they will display something like:
-----
Running: tests/test_udp_server
test_esp32spi_udp_server (TestUDPServer) ... skipped: Radio isn't an ESP32SPI
test_native_udp_server (TestUDPServer) ... Server started at: 192.168.xx.xx:5000 - waiting for UDP client connection.....
-----
Once you see "waiting for UDP client connection", it will add a "." every second until it get's a connection.
To make the connection, paste this method into a CPython terminal and call it with the IP and port from the test
"""


def udp_client_send(ip=None, port=None, timeout=60, message_loops=3):
    if ip is None:
        ip = input("IP? ")
    if port is None:
        port = input("Port? ")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(10)
        data = b"Hello World!"
        size = sock.sendto(data, (ip, port))
        print(f"UDP: Sent {size} bytes to {ip}:{port} - {data}")
        buffer = bytearray(64)
        for i in range(message_loops):
            start = time.monotonic()
            while True:
                elasped = time.monotonic()
                if int(elasped - start) > timeout:
                    break
                bytes_read, server_ip_address = sock.recvfrom_into(buffer)
                if bytes_read:
                    data = bytes(buffer[:bytes_read])
                    print(
                        f"UDP: Recieved {bytes_read} bytes from {server_ip_address} - {data}"
                    )
                    data = str(int(data) * 2).encode()
                    size = sock.sendto(data, (ip, port))
                    print(f"UDP: Sent {size} bytes to {ip}:{port} - {data}")
                    break
