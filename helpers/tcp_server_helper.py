# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import socket
import time

"""
When the TCP server tests are running they will display something like:
-----
Running: tests/test_tcp_server
test_esp32spi_tcp_server (TestTCPServer) ... skipped: Radio isn't an ESP32SPI
test_native_tcp_server (TestTCPServer) ... Server started at: 192.168.xx.xx:5000 - waiting for TCP client connection.....
-----
Once you see "waiting for TCP client connection", it will add a "." every second until it get's a connection.
To make the connection, paste this method into a CPython terminal and call it with the IP and port from the test
"""


def tcp_client_send(ip=None, port=None, timeout=60, message_loops=3):
    if ip is None:
        ip = input("IP? ")
    if port is None:
        port = input("Port? ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect((ip, port))
        data = b"Hello World!"
        size = sock.send(data)
        print(f"TCP: Sent {size} bytes to {ip}:{port} - {data}")
        buffer = bytearray(64)
        for i in range(message_loops):
            start = time.monotonic()
            while True:
                elasped = time.monotonic()
                if int(elasped - start) > timeout:
                    break
                bytes_read = sock.recv_into(buffer, len(buffer))
                if bytes_read:
                    data = bytes(buffer[:bytes_read])
                    print(f"TCP: Recieved {bytes_read} bytes from {ip}:{port} - {data}")
                    data = str(int(data) * 2).encode()
                    size = sock.send(data)
                    print(f"TCP: Sent {size} bytes to {ip}:{port} - {data}")
                    break
