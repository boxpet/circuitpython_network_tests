Welcome to circuitpython network tests' documentation!
======================================================

This project is currently a draft to see if this is a goo method to tests
network capabilities.

Setup
-----

1. From `CircuitPython_Unittest <https://github.com/mytechnotalent/CircuitPython_Unittest>`_ download the `unittest.py` and place it in the lib folder on your MCU

2. From `CircuitPython Scripts <https://github.com/boxpet/circuitpython_scripts/tree/main/circuitpython_scripts>`_ download the `connection_helper.py` and place it in the lib folder on your MCU

3. From this repo, copy the contents of the `code` folder onto the root of your MCU

4. Using `Circup <https://github.com/adafruit/circup>`_ install the requirements you your device: `circup install -r requirements-mcu.txt`

5. If you are testing the `ESP32SPI` or `WIZnet5k` you need to add `CIRCUITPY_PYSTACK_SIZE=3072` to your `settings.toml', otherwise you will get pystack failures

Running
-------

When you start the code and connect to the MCU, you will see something like this in the terminal:

.. code-block::

    ========================================
    Welcome to the network test runner
    ========================================

    Testing on:
    FeatherS3 with ESP32S3
    circuitpython v9.1.0
    unexpectedmaker_feathers3
    Has ssl: True

    Tests:
    1 test case(s) with  2 test(s) in: test_mqtt_connect.py
    1 test case(s) with  1 test(s) in: test_ntp.py
    1 test case(s) with  2 test(s) in: test_request_get.py
    1 test case(s) with  2 test(s) in: test_tcp_server.py
    1 test case(s) with  2 test(s) in: test_udp_server.py

    Total test cases: 5
    Total tests: 9

    Radio options:
    [0] Autodetect
    [1] Native
    [2] ESP32SPI
    [3] WIZnet5k
    Choose a radio [0-3]:

Select the radio option you want and press enter. From there you will see something like this:

.. code-block::

    Detecting radio...
    Found native Wifi
    Already connected
    IP Address:  192.168.xx.xx
    MAC address: XX:XX:XX:XX:XX:XX
    SSID:        Your-SSID
    RSSI:        -40
    Firmware:    n/a

    start tests?

Then enter `y` and they will start. A test run will look something like this:

.. code-block::

    ----------------------------------------

    Running: tests/test_ntp
    test_ntp (TestNTP) ... ok
    Ran 1 tests

    OK

    Code done running.

    Press any key to enter the REPL. Use CTRL-D to reload.
    Pretending to deep sleep until alarm, CTRL-C or file write.
    Woken up by alarm.

    Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.
    code.py output:

You'll have one of these for each test file. It sleeps after each one, to reset the memory and radio

for the tests in `test_tcp_server.py` and `test_udp_server`, check out the test file,
you will need to send a message to it for it to pass.

The final outpul will be something like:

.. code-block::

    ----------------------------------------

    Tests finished:
    test_mqtt_connect.py - passed: 2, failed: 0, errored: 0, skipped: 0, exceptioned: 0
    test_ntp.py - passed: 1, failed: 0, errored: 0, skipped: 0, exceptioned: 0
    test_request_get.py - passed: 2, failed: 0, errored: 0, skipped: 0, exceptioned: 0
    test_tcp_server.py - passed: 1, failed: 0, errored: 0, skipped: 1, exceptioned: 0
    test_udp_server.py - passed: 1, failed: 0, errored: 0, skipped: 1, exceptioned: 0
    passed:     7
    failed:     0
    errored:    0
    skipped:    2
    exceptions: 0

    Code done running.

    Press any key to enter the REPL. Use CTRL-D to reload.
