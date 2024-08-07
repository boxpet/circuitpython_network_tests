# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import sys
import time
import unittest

import adafruit_connection_manager
import alarm
import board
import supervisor
from connection_helper import enable_log, get_radio
from network_test_case import NetworkTestCase

from helpers import (
    RESULT_BLOCKS,
    RESULT_NOT_RUN,
    SLEEP_DELAY,
    TEST_PATH,
    ValidationMatrix,
    get_ipv4_address,
    get_radio_force,
    select_radio,
)

try:
    import ssl
except ImportError:
    ssl = None


class NetworkTests:
    def __init__(self, sleep_delay=SLEEP_DELAY):
        self._sleep_delay = sleep_delay
        self._test_files = []

    def board_info(self):
        machine = getattr(sys.implementation, "_machine", "Unknown")
        version = ".".join([str(part) for part in sys.implementation.version])
        has_ssl = "True" if ssl else False

        print()
        print(f"Testing on:")
        print(f" {machine}")
        print(f" {sys.implementation.name} v{version}")
        print(f" {board.board_id}")
        print(f" Has ssl: {has_ssl}")

    def find_test_files(self):
        self._test_files = os.listdir(TEST_PATH)
        self._test_files.sort()

    def finish(self):
        print("Tests finished:")

        all_validations = {
            validation: "U" for validation in ValidationMatrix.get_all_validations()
        }

        total_passed = 0
        total_failed = 0
        total_errored = 0
        total_skipped = 0
        total_exceptioned = 0
        for pos, test_file in enumerate(self._test_files, 1):
            test_file_path = self.get_import_name(test_file)
            validates = self.get_test_validates(test_file_path)

            test_pos = self.get_test_pos(pos)
            passed = alarm.sleep_memory[test_pos]
            failed = alarm.sleep_memory[test_pos + 1]
            errored = alarm.sleep_memory[test_pos + 2]
            skipped = alarm.sleep_memory[test_pos + 3]
            exceptioned = alarm.sleep_memory[test_pos + 4]

            if failed or errored or exceptioned:
                validation = "N"
            elif passed:
                validation = "Y"
            elif skipped:
                validation = "S"
            else:
                validation = "U"

            for validate in validates:
                all_validations[validate] = validation

            total_passed += passed
            total_failed += failed
            total_errored += errored
            total_skipped += skipped
            total_exceptioned += exceptioned

            print(f" {test_file} - ", end="")
            print(f"passed: {passed}, failed: {failed}, errored: {errored}, ", end="")
            print(f"skipped: {skipped}, exceptioned: {exceptioned}")

        print(f"passed:     {total_passed}")
        print(f"failed:     {total_failed}")
        print(f"errored:    {total_errored}")
        print(f"skipped:    {total_skipped}")
        print(f"exceptions: {total_exceptioned}")

        enable_log(False)
        self.board_info()
        self.radio_check()
        self.libary_versions()
        print()
        print("Validation:")
        for validation, result in all_validations.items():
            print(f" {validation:20}: {ValidationMatrix.TEST_RESULTS[result]}")

        alarm.sleep_memory[0] = 0

    def get_import_name(self, test_file):
        test_file = test_file.split(".")[0]
        return f"{TEST_PATH}/{test_file}"

    def get_test_count(self, test_suite):
        test_case_count = 0
        test_count = 0
        for test_case in test_suite.tests:
            test_case_count += 1
            for test_case_attribute in dir(test_case):
                if test_case_attribute.startswith("test"):
                    test_count += 1
        return test_case_count, test_count

    def get_test_pos(self, pos):
        return len(TEST_PATH) + 1 + ((pos - 1) * RESULT_BLOCKS)

    def get_test_suite(self, module_name):
        test_suite = unittest.TestSuite()
        imported_module = __import__(module_name, None, None, ["*"])
        for module_attribute in dir(imported_module):
            attribute = getattr(imported_module, module_attribute)
            if self.is_test_case(attribute):
                test_suite.addTest(attribute)
        return test_suite

    def get_test_validates(self, module_name):
        validates = []
        imported_module = __import__(module_name, None, None, ["*"])
        for module_attribute in dir(imported_module):
            attribute = getattr(imported_module, module_attribute)
            if self.is_test_case(attribute):
                validates.extend(attribute.VALIDATES)
        return validates

    def is_test_case(self, attribute):
        return (
            isinstance(attribute, type)
            and issubclass(attribute, unittest.TestCase)
            and attribute is not unittest.TestCase
            and attribute is not NetworkTestCase
        )

    def libary_versions(self):
        print()
        print("Library versions:")
        for library_full_name in [
            "adafruit_esp32spi.adafruit_esp32spi",
            "adafruit_minimqtt.adafruit_minimqtt",
            "adafruit_wiznet5k.adafruit_wiznet5k",
            "adafruit_connection_manager",
            "adafruit_ntp",
            "adafruit_requests",
        ]:
            try:
                library = __import__(library_full_name, None, None, ["*"])
                library_name = library_full_name.split(".")[0]
                print(f" {library_name}: {library.__version__}")
            except ImportError:
                pass

    def radio_check(self, pick=False):
        if pick:
            selected_radio = select_radio()
        else:
            selected_radio = None
        force_radio = get_radio_force(selected_radio)

        try:
            radio = get_radio(force=force_radio)
            pool = adafruit_connection_manager.get_radio_socketpool(radio)
            mac_addess = ":".join(f"{byte:02X}" for byte in radio.mac_address)

            try:
                if hasattr(radio, "ap_info"):
                    ssid = radio.ap_info.ssid
                    rssi = radio.ap_info.rssi
                else:
                    ssid = "n/a"
                    rssi = "n/a"
            except NotImplementedError:
                ssid = "unknown"
                rssi = "unknown"

            firmware = getattr(radio, "firmware_version", "n/a")
            chip = getattr(radio, "chip", "n/a")

            print()
            print("Radio info:")
            print(f" IP Address:  {get_ipv4_address(radio)}")
            print(f" MAC address: {mac_addess}")
            print(f" SSID:        {ssid}")
            print(f" RSSI:        {rssi}")
            print(f" Firmware:    {firmware}")
            print(f" Chip:        {chip}")

            return selected_radio

        except Exception as e:
            print(e)
            return -1

    def run_test(self, test_file, test_pos):
        test_file_path = self.get_import_name(test_file)
        print(f"Running: {test_file_path}")

        try:
            results = self.run_test_file(test_file_path)
            passed = results.testsRun - results.failuresNum - results.errorsNum
            failed = results.failuresNum
            errored = results.errorsNum
            skipped = results.skippedNum
            exceptioned = 0
        except Exception as e:
            print(e)
            passed = 0
            failed = 0
            errored = 0
            skipped = 0
            exceptioned = 1

        alarm.sleep_memory[test_pos] = passed
        alarm.sleep_memory[test_pos + 1] = failed
        alarm.sleep_memory[test_pos + 2] = errored
        alarm.sleep_memory[test_pos + 3] = skipped
        alarm.sleep_memory[test_pos + 4] = exceptioned
        supervisor.reload()

    def run_test_file(self, module_name):
        test_runner = unittest.TestRunner()
        test_suite = self.get_test_suite(module_name)
        results = test_runner.run(test_suite)

        return results

    def run_tests(self, new_run, selected_radio):
        print()
        print("----------------------------------------")
        print()

        if new_run:
            self.setup(selected_radio)
            print("Starting...")
            supervisor.reload()

        for pos, test_file in enumerate(self._test_files, 1):
            test_pos = self.get_test_pos(pos)
            if alarm.sleep_memory[test_pos] != RESULT_NOT_RUN:
                continue
            self.run_test(test_file, test_pos)

        self.finish()

    def setup(self, selected_radio):
        result_data = [RESULT_NOT_RUN] * (len(self._test_files) * RESULT_BLOCKS)
        initial_data = (
            [ord(c) for c in TEST_PATH]
            + [
                selected_radio,
            ]
            + result_data
        )
        for pos in range(len(initial_data)):
            alarm.sleep_memory[pos] = initial_data[pos]

    def start(self):
        self.find_test_files()

        run = False
        new_run = False
        selected_radio = None
        if bytes(alarm.sleep_memory[0 : len(TEST_PATH)]) != TEST_PATH.encode():
            print("========================================")
            print("Welcome to the network test runner")
            print("========================================")
            self.board_info()
            self.test_info()
            selected_radio = self.radio_check(pick=True)
            if selected_radio >= 0:
                print()
                start = input("start tests [y/n]? ").lower() == "y"
                if start:
                    new_run = True
                    run = True
        else:
            run = True

        if run:
            self.run_tests(new_run, selected_radio)

    def test_info(self):
        print()
        print("Tests:")
        total_test_case_count = 0
        total_test_count = 0
        for test_file in self._test_files:
            test_suite = self.get_test_suite(self.get_import_name(test_file))
            test_case_count, test_count = self.get_test_count(test_suite)
            total_test_case_count += test_case_count
            total_test_count += test_count
            print(
                f" {test_case_count:2} test case(s) with {test_count:2} test(s) in: {test_file}"
            )
        print()
        print(f"Total test cases: {total_test_case_count}")
        print(f"Total tests: {total_test_count}")
        print()


network_tests = NetworkTests()
network_tests.start()
