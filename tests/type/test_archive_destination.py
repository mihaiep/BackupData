import unittest
from datetime import datetime

from core.type import ArchiveDestination
from tests.utils import log_response, LOG


class TestArchiveDestination(unittest.TestCase):
    def setUp(self) -> None:
        self.dest = ArchiveDestination(
            "Test",
            "/dummy/path/",
            False,
            5,
            datetime(2020, 10, 20)
        )

    @log_response
    def test_init(self) -> None:
        self.assertEqual("Test", self.dest.label)
        self.assertEqual("/dummy/path", self.dest.path)
        self.assertEqual(False, self.dest.remote)
        self.assertEqual(5, self.dest.versions)
        self.assertEqual(datetime(2020, 10, 20), self.dest.last_run)

    @log_response
    def test_str(self) -> None:
        self.assertEqual(self.dest.label, str(self.dest))

    @log_response
    def test_display(self) -> None:
        display = self.dest.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue("Test" in display)
        self.assertTrue("/dummy/path" in display)
        self.assertTrue("@ Remote" not in display)
        self.assertTrue("versions: 5" in display)

        self.dest.remote = True
        display = self.dest.display()
        LOG.debug(f"Display: {display}")
        self.assertTrue("@ Remote" in display)

    @log_response
    def test_compare(self) -> None:
        another_dest = ArchiveDestination(
            "Another Label",
            "/dummy/path",
            False,
            10,
            datetime(2021, 5, 10)
        )
        LOG.debug(f"Compare {self.dest} - {another_dest}")
        self.assertEqual(self.dest, another_dest)
        self.assertNotEqual(self.dest.label, another_dest.label)
        self.assertEqual(self.dest.path, another_dest.path)
        self.assertEqual(self.dest.remote, another_dest.remote)
        self.assertNotEqual(self.dest.versions, another_dest.versions)
        self.assertNotEqual(self.dest.label, another_dest.last_run)

        another_dest.remote = not another_dest.remote
        self.assertNotEqual(self.dest, another_dest)

        another_dest.label = self.dest.label
        self.assertNotEqual(self.dest, another_dest)

        self.assertNotEqual(self.dest, 5)
