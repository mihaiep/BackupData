import base64
import binascii
import unittest
from datetime import datetime

from misc.utils import password_decrypt, password_encrypt, convert, VaultBackupException, handle_password, handle_timestamp
from tests.utils import log_response, LOG


class TestUtils(unittest.TestCase):

    @log_response
    def test_password_encrypt(self) -> None:
        password = "password"
        password_enc = password_encrypt(password)
        self.assertEqual(password_enc, base64.b64encode(password.encode()).decode())
        self.assertRaises(AttributeError, password_encrypt, None)

    @log_response
    def test_password_decrypt(self) -> None:
        password = "password"
        password_enc = password_encrypt(password)
        self.assertEqual(password, password_decrypt(password_enc))

        self.assertRaises(UnicodeDecodeError, password_decrypt, password)
        self.assertRaises(TypeError, password_decrypt, None)

    @log_response
    def test_convert_int(self) -> None:
        values = {
            1: [1, 1.0, 1.7, "1", "1.7", "+1", "+1.7"],
            0: [-0.9, 0.0, 0, +0.9, "-0.9", "-0.0", "0", "+0.0", "0.5", "+0.9"],
            -1: [-1, -1.9, "-1", "-1.0", "-1.4"],
            None: [None]
        }
        for expected in values.keys():
            for value in values.get(expected):
                LOG.debug("Converting: {:^5} -> {:^5}".format("None" if value is None else value, "None" if expected is None else expected))
                converted = convert(int, value)
                self.assertEqual(expected, converted)
        value_error = [
            False, "dsa", [1, 2, 3], {"a": 4}
        ]
        for value in value_error:
            LOG.debug("Expect error: {:^5} -> int".format("None" if value is None else str(value)))
            self.assertRaises(VaultBackupException, convert, int, value)

    @log_response
    def test_convert_float(self) -> None:
        values = {
            1.0: [1, 1.0, "1", "1.0", "+1", "+1.0"],
            1.7: [1.7, "1.7", "+1.7"],
            0.0: [-0.0, 0, "-0.0", "-0", "0", "+0", "+0.0"],
            -0.9: [-0.9, "-0.9"],
            None: [None]
        }
        for expected in values.keys():
            for value in values.get(expected):
                LOG.debug("Converting: {:^5} -> {:^5}".format("None" if value is None else value, "None" if expected is None else expected))
                converted = convert(float, value)
                self.assertEqual(expected, converted)
        value_error = [
            False, "dsa", [1, 2, 3], {"a": 4}
        ]
        for value in value_error:
            LOG.debug("Expect error: {:^5} -> int".format("None" if value is None else str(value)))
            self.assertRaises(VaultBackupException, convert, float, value)

    @log_response
    def test_convert_str(self) -> None:
        values = {
            "1": [1],
            "1.0": [1.0],
            "test": ["test"],
            "False": [False],
            "[1, 2, 3]": [[1, 2, 3]],
            "{'a': 4}": [{'a': 4}],
            None: [None]
        }
        for expected in values.keys():
            for value in values.get(expected):
                LOG.debug("Converting: {:^5} -> {:^5}".format("None" if value is None else str(value), "None" if expected is None else str(expected)))
                converted = convert(str, value)
                self.assertEqual(expected, converted)

    @log_response
    def test_convert_bool(self) -> None:
        values = {
            False: [0, "0", "false", "FALSE", "no", False],
            True: [1, "1", "true", "TRUE", "yes", True],
            None: [None]
        }
        for expected in values.keys():
            for value in values.get(expected):
                LOG.debug("Converting: {:^5} -> {:^5}".format("None" if value is None else value, "None" if expected is None else expected))
                converted = convert(bool, value)
                self.assertEqual(expected, converted)
        value_error = [
            0.0, '-0', "+0", 1.0, "1.0", "+1", "+1.0", "dsa", [1, 2, 3], {"a": 4}
        ]
        for value in value_error:
            LOG.debug("Expect error: {:^5} -> int".format("None" if value is None else str(value)))
            self.assertRaises(VaultBackupException, convert, bool, value)

    @log_response
    def test_convert_other(self) -> None:
        value_error = [
            [1, 2, 3], {"a": 4}
        ]
        for c_type in [int, float, bool]:
            for value in value_error:
                LOG.debug("Expect error: {:^5} -> {}".format("None" if value is None else str(value), str(c_type)))
                self.assertRaises(VaultBackupException, convert, type, value)

    @log_response
    def test_handle_password(self) -> None:
        password = "test123"
        password_encrypted = password_encrypt(password)

        result = handle_password(f"enc({password})")
        self.assertEqual(password_encrypted, result)

        result = handle_password(f"encrypt({password})")
        self.assertEqual(password_encrypted, result)

        result = handle_password(f"{password_encrypted}")
        self.assertEqual(password_encrypted, result)

        result = handle_password(None)
        self.assertEqual(None, result)

        self.assertRaises(binascii.Error, handle_password, f"{password})")

    @log_response
    def test_handle_timestamp(self) -> None:
        self.assertEqual(datetime(2020, 10, 20), handle_timestamp("2020-10-20T00:00:00.000000"))
        self.assertEqual(datetime(2020, 10, 20), handle_timestamp("2020-10-20 00:00:00"))
        self.assertEqual(datetime(2020, 10, 20), handle_timestamp("2020-10-20"))
        self.assertEqual(datetime(1900, 1, 1), handle_timestamp(None))
        self.assertRaises(ValueError, handle_timestamp, "2020-10-20 00:00:")
