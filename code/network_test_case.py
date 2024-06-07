# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers
#
# SPDX-License-Identifier: MIT

import os
import traceback
from unittest import SkipTest, TestCase

from helpers import get_radio_force

FORCE_RADIO = os.getenv("NETWORK_TEST_FORCE_RADIO", get_radio_force())


class NetworkTestCase(TestCase):
    def setUp(self):
        import adafruit_connection_manager
        from connection_helper import enable_log, get_radio

        enable_log(False)
        self.radio = get_radio(force=FORCE_RADIO)
        self.pool = adafruit_connection_manager.get_radio_socketpool(self.radio)
        self.ssl_context = adafruit_connection_manager.get_radio_ssl_context(self.radio)

    def tearDown(self):
        import adafruit_connection_manager

        adafruit_connection_manager.connection_manager_close_all()

    def run(self, result: TestResult):
        for name in dir(self):
            if name.startswith("test"):
                print(f"{name} ({self.__qualname__}) ...", end="")  # report progress
                test_method = getattr(self, name)
                self.setUp()  # Pre-test setup (every test)
                try:
                    result.testsRun += 1
                    test_method()
                    print(" ok")
                except SkipTest as e:
                    print(" skipped:", e.args[0])
                    result.skippedNum += 1
                    result.testsRun -= 1  # not run if skipped
                except AssertionError as e:
                    print(" FAIL:", e.args[0] if e.args else "no assert message")
                    result.failuresNum += 1
                except (SystemExit, KeyboardInterrupt):
                    raise
                except Exception as e:  # noqa
                    print(" ERROR", type(e).__name__)
                    print("".join(traceback.format_exception(e)))
                    result.errorsNum += 1
                finally:
                    self.tearDown()  # Post-test teardown (every test)
