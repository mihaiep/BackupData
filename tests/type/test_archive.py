import unittest
from datetime import datetime

from core.type import Archive, ArchiveDestination
from misc.utils import password_encrypt, VaultBackupException
from tests.utils import log_response, LOG


# noinspection SpellCheckingInspection
class TestArchive(unittest.TestCase):

    def setUp(self) -> None:
        self.archive = Archive(
            "test_archive.zip",
            "/dummy/path/"
        )
        self.archive.set_password(password_encrypt("test123"))
        self.archive.add_destination("Test", "/dummy2/path/", False, 5, datetime(2020, 10, 20))

    @log_response
    def test_init(self) -> None:
        self.assertEqual("test_archive.zip", self.archive.name)
        self.assertEqual("/dummy/path", self.archive.path)
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("test123", self.archive.get_password(True))
        self.assertEqual(password_encrypt("test123"), self.archive.get_password(False))

        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(5, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[0].last_run)

    @log_response
    def test_str(self) -> None:
        self.assertTrue("test_archive.zip" in str(self.archive))
        self.assertTrue("/dummy/path" in str(self.archive))

    @log_response
    def test_compare(self) -> None:
        another_archive = Archive(
            "test_archive.zip",
            "/dummy/path/"
        )
        self.assertNotEqual(self.archive, another_archive)

        another_archive = Archive(
            "test_archive.zip",
            "/dummy/pathf/"
        )
        another_archive.set_password(password_encrypt("test123"))
        self.assertNotEqual(self.archive, another_archive)

        another_archive = Archive(
            "test_archive_2.zip",
            "/dummy/path/"
        )
        another_archive.set_password(password_encrypt("test123"))
        self.assertNotEqual(self.archive, another_archive)

        another_archive = Archive(
            "test_archive.zip",
            "/dummy/path/"
        )
        another_archive.set_password(password_encrypt("test123"))
        self.assertEqual(self.archive, another_archive)

        self.assertNotEqual(self.archive, 5)

    @log_response
    def test_get_archive_path(self) -> None:
        timestamp = "20201010_000000"
        date_timestamp = datetime(2020, 10, 10)
        self.assertEqual(f"{Archive.dir_path}/test_archive_{timestamp}.zip", self.archive.get_archive_path(date_timestamp))

    @log_response
    def test_add_destination(self) -> None:
        self.assertEqual(1, len(self.archive.destinations))

        LOG.debug("Add same destination")
        self.archive.add_destination("Test", "/dummy2/path/", False, 5, datetime(2020, 10, 20))
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(5, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[0].last_run)

        ########################################################
        LOG.debug("Add destination different version | smaller")
        self.archive.add_destination("Test", "/dummy2/path/", False, 3, datetime(2020, 10, 20))
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(5, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[0].last_run)

        ########################################################
        LOG.debug("Add destination different version | bigger")
        self.archive.add_destination("Test", "/dummy2/path/", False, 7, datetime(2020, 10, 20))
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(7, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[0].last_run)

        ########################################################
        LOG.debug("Add destination different last_run | after")
        self.archive.add_destination("Test", "/dummy2/path/", False, 7, datetime(2020, 11, 20))
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(7, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[0].last_run)

        ########################################################
        LOG.debug("Add destination different last_run | before")
        self.archive.add_destination("Test", "/dummy2/path/", False, 7, datetime(2020, 5, 20))
        self.assertEqual(1, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(7, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 5, 20), self.archive.destinations[0].last_run)

        ############################################
        LOG.debug("Add destination different label")
        self.assertRaises(VaultBackupException, self.archive.add_destination, "Test2", "/dummy2/path/", False, 7, datetime(2020, 5, 20))

        ####################################
        LOG.debug("Insert same Destination")
        destination = ArchiveDestination("Test", "/dummy2/path/", False, 5, datetime(2020, 10, 20))
        self.archive.insert_destination(destination)
        self.assertEqual(1, len(self.archive.destinations))

        ###################################
        LOG.debug("Insert new destination")
        destination.remote = True
        self.archive.insert_destination(destination)
        self.assertEqual(2, len(self.archive.destinations))
        self.assertEqual("Test", self.archive.destinations[0].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[0].path)
        self.assertEqual(False, self.archive.destinations[0].remote)
        self.assertEqual(7, self.archive.destinations[0].versions)
        self.assertEqual(datetime(2020, 5, 20), self.archive.destinations[0].last_run)
        self.assertEqual("Test", self.archive.destinations[1].label)
        self.assertEqual("/dummy2/path", self.archive.destinations[1].path)
        self.assertEqual(True, self.archive.destinations[1].remote)
        self.assertEqual(5, self.archive.destinations[1].versions)
        self.assertEqual(datetime(2020, 10, 20), self.archive.destinations[1].last_run)

    @log_response
    def test_display(self) -> None:
        display = self.archive.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue(display.count('\n') == 2)
        self.assertTrue(self.archive.name in display)
        self.assertTrue(self.archive.path in display)
        self.assertTrue("Destination:" in display)
        self.assertTrue(self.archive.destinations[0].label in display)
        self.assertTrue(self.archive.destinations[0].path in display)
        self.assertTrue(f"versions: {self.archive.destinations[0].versions}" in display)
        self.assertTrue("@ Remote" not in display)

        LOG.debug("Change destination to remote")
        self.archive.destinations[0].remote = True
        display = self.archive.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue(display.count('\n') == 2)
        self.assertTrue(self.archive.name in display)
        self.assertTrue(self.archive.path in display)
        self.assertTrue("Destination:" in display)
        self.assertTrue(self.archive.destinations[0].label in display)
        self.assertTrue(self.archive.destinations[0].path in display)
        self.assertTrue(f"versions: {self.archive.destinations[0].versions}" in display)
        self.assertTrue("@ Remote" in display)

        LOG.debug("Add new local destination")
        self.archive.add_destination("zLabel", "/zpath/here", False, 2, datetime(2000, 1, 13))
        display = self.archive.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue(display.count('\n') == 4)
        self.assertTrue(self.archive.name in display)
        self.assertTrue(self.archive.path in display)
        self.assertTrue("Destinations:" in display)
        self.assertTrue(self.archive.destinations[0].label in display)
        self.assertTrue(self.archive.destinations[0].path in display)
        self.assertTrue(f"versions: {self.archive.destinations[0].versions}" in display)
        self.assertTrue("@ Remote" in display.split('\n')[-2])
        self.assertTrue(self.archive.destinations[1].label in display)
        self.assertTrue(self.archive.destinations[1].path in display)
        self.assertTrue(f"versions: {self.archive.destinations[1].versions}" in display)
        self.assertTrue("@ Remote" not in display.split('\n')[-1])
