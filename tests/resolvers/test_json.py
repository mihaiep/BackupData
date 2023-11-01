import json
import os.path
import unittest
from datetime import datetime
from unittest.mock import patch

from core.resolvers import JsonResolver
from misc.utils import VaultBackupException
from tests.utils import log_response, LOG


class TestJsonResolver(unittest.TestCase):

    def setUp(self) -> None:
        file_path = "resolver.json" if os.path.isfile("resolver.json") else "resolvers/resolver.json"
        with open(file_path, 'r') as json_file:
            self.base_json = json.loads(json_file.read())
        patch('core.resolvers.open').start()

        self.mock_json = patch('core.resolvers.json').start()
        self.mock_sys = patch('core.resolvers.sys').start()

        self.mock_sys.argv = ["/dummy/path"]
        self.mock_json.loads.return_value = self.base_json

    @log_response
    def test_init(self) -> None:
        json_resolver = JsonResolver()
        LOG.info('\n' + json.dumps(json_resolver.to_json(), indent='\t'))
        self.assertEqual(True, json_resolver.force)
        # SSH
        self.assertEqual("dummy", json_resolver.ssh.user)
        self.assertEqual("password_dummy", json_resolver.ssh.get_password())
        self.assertEqual("0.0.0.0", json_resolver.ssh.ip)
        self.assertEqual("22", json_resolver.ssh.port)
        self.assertEqual(True, json_resolver.require_ssh)
        # Backup
        self.assertEqual(1, len(json_resolver.backups))
        self.assertEqual("backup.zip", json_resolver.backups[0].name)
        self.assertEqual("/dummy/path", json_resolver.backups[0].path)
        self.assertEqual("archive_password", json_resolver.backups[0].get_password())
        # Destination
        self.assertEqual(1, len(json_resolver.backups[0].destinations))
        self.assertEqual("Prefer to not", json_resolver.backups[0].destinations[0].label)
        self.assertEqual("/not/again", json_resolver.backups[0].destinations[0].path)
        self.assertEqual(True, json_resolver.backups[0].destinations[0].remote)
        self.assertEqual(1, json_resolver.backups[0].destinations[0].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[0].destinations[0].last_run)

    @log_response
    def test_init_with_two_destinations(self) -> None:
        self.base_json['backup'][0]['destination'].append({
            "label": "Another Dest",
            "path": "/here/we/go",
            "remote": "false",
            "versions": "1",
            "last_run": None
        })
        json_resolver = JsonResolver()
        LOG.info('\n' + json.dumps(json_resolver.to_json(), indent='\t'))
        self.assertEqual(2, len(json_resolver.backups[0].destinations))
        self.assertEqual("Another Dest", json_resolver.backups[0].destinations[1].label)
        self.assertEqual("/here/we/go", json_resolver.backups[0].destinations[1].path)
        self.assertEqual(False, json_resolver.backups[0].destinations[1].remote)
        self.assertEqual(1, json_resolver.backups[0].destinations[1].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[0].destinations[1].last_run)

    @log_response
    def test_init_with_two_backups(self) -> None:
        self.base_json['backup'].append({
            "name": "backup2.zip",
            "path": "/dummy/path2",
            "password": "enc(archive_password)",
            "destination": [{
                "label": "Another Dest",
                "path": "/here/we/go",
                "remote": "false",
                "versions": "1",
                "last_run": None
            }]
        })
        json_resolver = JsonResolver()
        LOG.info('\n' + json.dumps(json_resolver.to_json(), indent='\t'))
        self.assertEqual(2, len(json_resolver.backups))
        # Backup 1
        self.assertEqual("backup.zip", json_resolver.backups[0].name)
        self.assertEqual("/dummy/path", json_resolver.backups[0].path)
        self.assertEqual("archive_password", json_resolver.backups[0].get_password())
        # Backup 2
        self.assertEqual("backup2.zip", json_resolver.backups[1].name)
        self.assertEqual("/dummy/path2", json_resolver.backups[1].path)
        self.assertEqual("archive_password", json_resolver.backups[1].get_password())
        # Destination 1 - 1
        self.assertEqual(1, len(json_resolver.backups[0].destinations))
        self.assertEqual("Prefer to not", json_resolver.backups[0].destinations[0].label)
        self.assertEqual("/not/again", json_resolver.backups[0].destinations[0].path)
        self.assertEqual(True, json_resolver.backups[0].destinations[0].remote)
        self.assertEqual(1, json_resolver.backups[0].destinations[0].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[0].destinations[0].last_run)
        # Destination 2 - 1
        self.assertEqual(1, len(json_resolver.backups[1].destinations))
        self.assertEqual("Another Dest", json_resolver.backups[1].destinations[0].label)
        self.assertEqual("/here/we/go", json_resolver.backups[1].destinations[0].path)
        self.assertEqual(False, json_resolver.backups[1].destinations[0].remote)
        self.assertEqual(1, json_resolver.backups[1].destinations[0].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[1].destinations[0].last_run)

    @log_response
    def test_init_with_two_identical_backups_with_different_destinations(self) -> None:
        self.base_json['backup'].append({
            "name": "backup.zip",
            "path": "/dummy/path",
            "password": "enc(archive_password)",
            "destination": [{
                "label": "Another Dest",
                "path": "/here/we/go",
                "remote": "false",
                "versions": "1",
                "last_run": None
            }]
        })
        json_resolver = JsonResolver()
        LOG.info('\n' + json.dumps(json_resolver.to_json(), indent='\t'))
        # SSH
        self.assertEqual("dummy", json_resolver.ssh.user)
        self.assertEqual("password_dummy", json_resolver.ssh.get_password())
        self.assertEqual("0.0.0.0", json_resolver.ssh.ip)
        self.assertEqual("22", json_resolver.ssh.port)
        self.assertEqual(True, json_resolver.require_ssh)
        # Backup
        self.assertEqual(1, len(json_resolver.backups))
        self.assertEqual("backup.zip", json_resolver.backups[0].name)
        self.assertEqual("/dummy/path", json_resolver.backups[0].path)
        self.assertEqual("archive_password", json_resolver.backups[0].get_password())
        self.assertEqual(2, len(json_resolver.backups[0].destinations))
        # Destination 1
        self.assertEqual("Prefer to not", json_resolver.backups[0].destinations[0].label)
        self.assertEqual("/not/again", json_resolver.backups[0].destinations[0].path)
        self.assertEqual(True, json_resolver.backups[0].destinations[0].remote)
        self.assertEqual(1, json_resolver.backups[0].destinations[0].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[0].destinations[0].last_run)
        # Destination 2
        self.assertEqual("Another Dest", json_resolver.backups[0].destinations[1].label)
        self.assertEqual("/here/we/go", json_resolver.backups[0].destinations[1].path)
        self.assertEqual(False, json_resolver.backups[0].destinations[1].remote)
        self.assertEqual(1, json_resolver.backups[0].destinations[1].versions)
        self.assertEqual(datetime(1900, 1, 1), json_resolver.backups[0].destinations[1].last_run)

    @log_response
    def test_wrong_key(self) -> None:
        self.base_json["z"] = 1
        self.assertRaises(VaultBackupException, JsonResolver)
