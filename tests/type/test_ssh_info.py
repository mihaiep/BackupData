import unittest

from core.type import SSHInfo
from misc.utils import password_encrypt
from tests.utils import log_response, LOG


class TestSSHInfo(unittest.TestCase):

    def setUp(self) -> None:
        self.ssh = SSHInfo("admin", "255.255.255.255", "22")
        self.ssh.set_password(password_encrypt("admin_pass"))

    @log_response
    def test_init(self) -> None:
        self.assertEqual("admin", self.ssh.user)
        self.assertEqual("255.255.255.255", self.ssh.ip)
        self.assertEqual("22", self.ssh.port)
        self.assertEqual("admin_pass", self.ssh.get_password(True))
        self.assertEqual(password_encrypt("admin_pass"), self.ssh.get_password(False))

    @log_response
    def test_display(self) -> None:
        display = self.ssh.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue(self.ssh.user in display)
        self.assertTrue(self.ssh.ip in display)
        self.assertTrue(self.ssh.port in display)
        self.assertTrue("admin_pass" not in display)
        self.assertTrue(password_encrypt("admin_pass") not in display)

    @log_response
    def test_null_password(self) -> None:
        self.ssh.set_password(None)
        self.assertIsNone(self.ssh.get_password(True))
        self.assertIsNone(self.ssh.get_password(False))
