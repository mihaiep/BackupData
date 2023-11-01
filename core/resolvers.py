import json
import re
import sys
from typing import Optional, List

from core.type import SSHInfo, Archive
from misc.logger import LOGGER
from misc.utils import VaultBackupException, convert, handle_password, handle_timestamp, not_none


# noinspection SpellCheckingInspection
class ArgsResolver:
    __ARG_LIST = ["force", "password", "password_ssh"]

    def __init__(self) -> None:
        self.force = None
        self.password = None
        self.password_ssh = None
        LOGGER.debug(f"System args: {sys.argv}")
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                matches = re.findall(r"-D([a-z_A-Z]+)=(.+)", arg)
                if len(matches) == 0:
                    raise VaultBackupException(f"Input argument '{arg}' is not correctly formatted. Expected: -Dargument='value' or -Dargument=value.\nSupported arguments: {ArgsResolver.__ARG_LIST}")
                key, value = matches[0]
                if key not in ArgsResolver.__ARG_LIST:
                    raise VaultBackupException(f"Argument '{key}' is not supported.")
                if key == "force":
                    self.force = not_none(key, convert(bool, value))
                    LOGGER.debug(f"Force set to: {self.force}")
                elif key == "password":
                    self.password = not_none(key, handle_password(value))
                    LOGGER.debug(f"Password was set")
                elif key == "password_ssh":
                    self.password_ssh = not_none(key, handle_password(value))
                    LOGGER.debug(f"SSH password was set")


class JsonResolver:
    __ARG_LIST = ["force", "ssh", "backup"]

    def __init__(self, json_path: str = "config.json"):
        self.force: bool = False
        self.ssh: Optional[SSHInfo] = None
        self.backups: List[Archive] = []

        self.require_ssh = False
        self.__handle_data(json_path)
        if self.require_ssh and self.ssh is None:
            raise VaultBackupException("Current configuration require a SSH connection, but no SSH info was provided.")

    def __handle_data(self, json_path: str):
        self.__data: dict = json.loads(open(json_path, 'r').read())
        for key in self.__data.keys():
            if key not in JsonResolver.__ARG_LIST:
                raise VaultBackupException(f"JSON key '{key}' is not supported.")
            if key == "force":
                force = convert(bool, self.__data.get(key))
                if force:
                    self.force = True
                LOGGER.info(f"Force run: {self.force}")
            elif key == "ssh":
                ssh = self.__data.get(key)
                self.ssh = SSHInfo(
                    not_none(key + ".user", ssh.get("user")),
                    not_none(key + ".ip", ssh.get("ip")),
                    not_none(key + ".port", ssh.get("port"))
                )
                self.ssh.set_password(handle_password(ssh.get("password")))
            elif key == "backup":
                for backup in self.__data.get(key):
                    parent_path = f"{key}[{self.__data.get(key).index(backup)}]"
                    crt_backup = Archive(
                        not_none(f'{parent_path}.name', convert(str, backup.get("name"))),
                        not_none(f'{parent_path}.path', convert(str, backup.get("path")))
                    )
                    crt_backup.set_password(handle_password(backup.get("password")))

                    if crt_backup in self.backups:
                        crt_backup = self.backups[self.backups.index(crt_backup)]
                    else:
                        self.backups.append(crt_backup)

                    for dst in backup.get("destination"):
                        self.require_ssh = self.require_ssh or convert(bool, dst.get("remote"))
                        crt_backup.add_destination(
                            not_none(f"{parent_path}.destination.label", convert(str, dst.get("label"))),
                            not_none(f"{parent_path}.destination.path", convert(str, dst.get("path"))),
                            not_none(f"{parent_path}.destination.remote", convert(bool, dst.get("remote"))),
                            not_none(f"{parent_path}.destination.versions", convert(int, dst.get("versions"))),
                            handle_timestamp(dst.get("last_run"))
                        )
        self._update_backup_struct()
        args_resolver = ArgsResolver()
        if args_resolver.force is not None:
            self.force = args_resolver.force
        if args_resolver.password_ssh is not None:
            self.ssh.set_password(args_resolver.password_ssh)
        if args_resolver.password is not None:
            [bkp.set_password(args_resolver.password) for bkp in self.backups]

    def update_last_run_date(self) -> None:
        for bkp in self.backups:
            for dst in bkp.destinations:
                self.__data['backup'][self.backups.index(bkp)]['destination'][bkp.destinations.index(dst)]['last_run'] = dst.last_run.isoformat()

    def _update_backup_struct(self) -> None:
        backups = []
        for bkp in self.backups:
            backups.append({
                "name": bkp.name,
                "path": bkp.path,
                "password": bkp.get_password(False),
                "destination": [{
                    "label": dst.label,
                    "path": dst.path,
                    "remote": dst.remote,
                    "versions": dst.versions,
                    "last_run": dst.last_run.isoformat()
                } for dst in bkp.destinations]
            })
        self.__data['backup'] = backups

    def to_json(self) -> dict:
        return {
            "force": self.force,
            "ssh": {
                "user": self.ssh.user,
                "password": self.ssh.get_password(False),
                "ip": self.ssh.ip,
                "port": self.ssh.port
            },
            "backup": [
                {
                    "name": x.name,
                    "path": x.path,
                    "password": x.get_password(False),
                    "destination": [
                        {
                            "label": y.label,
                            "path": y.path,
                            "remote": y.remote,
                            "versions": y.versions,
                            "last_run": y.last_run.isoformat()
                        } for y in x.destinations
                    ]
                } for x in self.backups
            ]
        }
