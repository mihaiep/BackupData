import binascii
import unittest
from unittest.mock import patch

from core.resolvers import ArgsResolver
from misc.utils import password_encrypt, VaultBackupException
from tests.utils import log_response


# noinspection SpellCheckingInspection
class TestArgResolver(unittest.TestCase):
    @log_response
    def test_no_args(self) -> None:
        sys_patch = patch("core.resolvers.sys")
        sys_mock = sys_patch.start()
        sys_mock.argv = ["/dummy/path"]

        args = ArgsResolver()
        self.assertIsNone(args.force)
        self.assertIsNone(args.password)
        self.assertIsNone(args.password_ssh)

    @log_response
    def test_with_args(self) -> None:
        sys_patch = patch("core.resolvers.sys")
        sys_mock = sys_patch.start()

        sys_mock.argv = ["/dummy/path", "-Dforce=false"]
        args = ArgsResolver()
        self.assertEqual(False, args.force)
        self.assertIsNone(args.password)
        self.assertIsNone(args.password_ssh)

        sys_mock.argv = ["/dummy/path", "-Dpassword=enc(test)"]
        args = ArgsResolver()
        self.assertIsNone(args.force)
        self.assertEqual(password_encrypt("test"), args.password)
        self.assertIsNone(args.password_ssh)

        sys_mock.argv = ["/dummy/path", "-Dpassword_ssh=enc(test)"]
        args = ArgsResolver()
        self.assertIsNone(args.force)
        self.assertIsNone(args.password)
        self.assertEqual(password_encrypt("test"), args.password_ssh)

        sys_mock.argv = ["/dummy/path", "-Dforce=yes", "-Dpassword=enc(test)", f"-Dpassword_ssh={password_encrypt('test1')}"]
        args = ArgsResolver()
        self.assertEqual(True, args.force)
        self.assertEqual(password_encrypt("test"), args.password)
        self.assertEqual(password_encrypt("test1"), args.password_ssh)

    @log_response
    def test_wrong_args(self) -> None:
        sys_patch = patch("core.resolvers.sys")
        sys_mock = sys_patch.start()

        sys_mock.argv = ["/dummy/path", "-Dforce=g"]
        self.assertRaises(VaultBackupException, ArgsResolver)

        sys_mock.argv = ["/dummy/path", "-Dpassword=test"]
        self.assertRaises(UnicodeDecodeError, ArgsResolver)

        sys_mock.argv = ["/dummy/path", "-Dpassword_ssh=g"]
        self.assertRaises(binascii.Error, ArgsResolver)

        sys_mock.argv = ["/dummy/path", "-Sforce=true"]
        self.assertRaises(VaultBackupException, ArgsResolver)

        sys_mock.argv = ["/dummy/path", "-Dskip=all"]
        self.assertRaises(VaultBackupException, ArgsResolver)
