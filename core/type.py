import os.path
import re
from datetime import datetime
from typing import Optional, List

from misc.logger import LOGGER
from misc.utils import password_decrypt, VaultBackupException


class SSHInfo:
    """SSH Connection Info"""

    def __init__(self, user: str, ip: str, port: str):
        self.user: str = user
        self.__password: Optional[str] = None
        self.ip: str = ip
        self.port: str = port
        LOGGER.debug(f"Initialized SSHInfo: {self}")

    def __str__(self) -> str:
        return self.user

    def get_password(self, decrypt: bool = True) -> str:
        return self.__password if self.__password is None else password_decrypt(self.__password) if decrypt else self.__password

    def set_password(self, password: Optional[str]) -> None:
        """Expects encrypted password"""
        self.__password = password

    def display(self, indent: str = "") -> str:
        return indent + f"{self.user}@{self.ip}:{self.port}"


class ArchiveDestination:
    """Information about where archived data is going to be stored."""

    def __init__(self, label: str, path: str, remote: bool, versions: int, last_run: datetime):
        self.label: str = label
        self.path: str = os.path.abspath(path)
        self.remote: bool = remote
        self.versions: int = versions
        self.last_run: datetime = last_run
        self.is_eligible = False
        if versions <= 0:
            raise VaultBackupException("Versions number must be at least 1.")
        LOGGER.debug(f"Initialized Archive Destination: {self}")

    def __str__(self) -> str:
        return self.label

    def __eq__(self, other) -> bool:
        return False if not isinstance(other, ArchiveDestination) else \
            True if self.__hash__() == other.__hash__() else False

    def __hash__(self) -> int:
        return "{}{}".format(self.path, self.remote).__hash__()

    def display(self, indent: str = "") -> str:
        return indent + "[{}{}] {} - versions: {}".format(self.label, " @ Remote" if self.remote else "", self.path, self.versions)


class Archive:
    dir_path = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])

    def __init__(self, name: str, path: str):
        self.name: str = name
        self.path: str = os.path.abspath(path)
        self.destinations: List[ArchiveDestination] = []
        self.__password: Optional[str] = None
        self.__archive_path: Optional[str] = None
        if not re.match(r".+\.zip", self.name):
            raise VaultBackupException("Archive name doesnt match the pattern: <filename>.zip")
        LOGGER.debug(f"Initialized Archive: {self}")

    def __str__(self) -> str:
        return f"{self.name} [{self.path}]"

    def __eq__(self, other) -> bool:
        return False if not isinstance(other, Archive) else \
            False if self.__hash__() != other.__hash__() else True

    def __hash__(self) -> int:
        return (self.name + self.path + (self.__password if self.__password is not None else "")).__hash__()

    def get_archive_path(self, start_time: datetime = None) -> str:
        if self.__archive_path is None:
            name = ".".join(self.name.split(".")[:-1])
            date_format = start_time.strftime("%Y%m%d_%H%M%S")
            self.__archive_path = os.path.join(Archive.dir_path, f"{name}_{date_format}.zip")
        return self.__archive_path

    def get_password(self, decrypt: bool = True) -> str:
        return self.__password if self.__password is None else password_decrypt(self.__password) if decrypt else self.__password

    def set_password(self, password: str) -> None:
        """Expects encrypted password"""
        self.__password = password

    def add_destination(self, label: str, path: str, remote: bool, versions: int, last_run: datetime):
        dst = ArchiveDestination(label, path, remote, versions, last_run)
        self.insert_destination(dst)

    def insert_destination(self, dst: ArchiveDestination):
        if dst not in self.destinations:
            self.destinations.append(dst)
        else:
            self.__merge(dst)

    def __merge(self, new_dst: ArchiveDestination):
        index = self.destinations.index(new_dst)
        if self.destinations[index].label != new_dst.label:
            raise VaultBackupException(f"Label conflict between {self.destinations[index]} and {new_dst}")
        self.destinations[index].versions = max(self.destinations[index].versions, new_dst.versions)
        self.destinations[index].last_run = min(self.destinations[index].last_run, new_dst.last_run)

    def display(self, indent: str = "") -> str:
        return indent + (f"Archive: {self.name}\n"
                         f"Path: {self.path}\n" +
                         "{}".format('Destination: ' if len(self.destinations) <= 1 else 'Destinations:\n\t') +
                         "\n\t".join(map(lambda x: x.display(), self.destinations))).replace("\n", f"\n{indent}")
