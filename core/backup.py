import os
from datetime import datetime
from shutil import copy2
from typing import List

import pyzipper

from core.ssh import SSHConnection
from core.type import Archive, SSHInfo
from misc.utils import LOGGER


class BackupExecutor:
    def __init__(self, force: bool, require_ssh: bool, ssh: SSHInfo):
        self.__force = force
        self.__ssh = SSHConnection(ssh) if require_ssh else None

    def execute(self, archives: List[Archive]):
        for archive in archives:
            start_time = datetime.now()
            LOGGER.info(f"Execution started for\n{archive.display()}")
            is_eligible = self._get_eligible_destinations(archive)
            eligible_indexes = list(filter(lambda x: is_eligible[x], range(0, len(archive.destinations))))
            allow_execution = True in is_eligible
            LOGGER.debug(f"Allow execution: {allow_execution}")
            if allow_execution:
                try:
                    self._do_archive(archive, start_time)
                    self._copy_archive(archive, eligible_indexes)
                    self._clean_archives(archive)
                    for dst in archive.destinations:
                        dst.last_run = start_time
                finally:
                    self._delete_archive(archive)

    def _get_eligible_destinations(self, archive: Archive) -> list:
        LOGGER.debug("Getting eligible destinations")
        if self.__force:
            return [True] * len(archive.destinations)

        destinations_num = len(archive.destinations)
        is_eligible = [False] * destinations_num
        last_run = [i.last_run for i in archive.destinations]

        for crt_path, dirs, files in os.walk(os.path.abspath(archive.path)):
            crt_list = files
            crt_list.extend(dirs)
            for elem in crt_list:
                for index in range(0, destinations_num):
                    if is_eligible[index] is not True and datetime.fromtimestamp(os.path.getmtime(os.path.join(crt_path, elem))) >= last_run[index]:
                        is_eligible[index] = True
                if is_eligible.count(True) == destinations_num:
                    return is_eligible
        return is_eligible

    # noinspection PyMethodMayBeStatic
    def _do_archive(self, archive: Archive, start_time: datetime) -> None:
        LOGGER.info(f"Archiving local data to: {archive.get_archive_path(start_time)}")
        with pyzipper.AESZipFile(
                archive.get_archive_path(start_time), 'w',
                compression=pyzipper.ZIP_DEFLATED
        ) as zip_file:
            if archive.get_password() is not None:
                LOGGER.debug("Setting up password")
                zip_file.encryption = pyzipper.WZ_AES
                zip_file.pwd = archive.get_password().encode()
            for crt_path, directories, files in os.walk(archive.path):
                for directory in directories:
                    abs_path = os.path.abspath(os.path.join(crt_path, directory))
                    rel_path = os.path.relpath(abs_path, archive.path)
                    LOGGER.debug(f"Writing Dir : {rel_path}")
                    zip_file.write(abs_path, rel_path)
                for file in files:
                    abs_path = os.path.abspath(os.path.join(crt_path, file))
                    rel_path = os.path.relpath(abs_path, archive.path)
                    LOGGER.debug(f"Writing File: {rel_path}")
                    zip_file.write(abs_path, rel_path)
        LOGGER.info(f"Archive was crated: {archive.get_archive_path()}")

    def _copy_archive(self, archive: Archive, eligible_indexes: list) -> None:
        LOGGER.debug("Copying zip file")
        for index in eligible_indexes:
            destination = archive.destinations[index]
            if destination.remote:
                LOGGER.info(f"[{destination.label}] Uploading '{archive.get_archive_path()}' to '{destination.path}'")
                self.__ssh.upload(archive.get_archive_path(), destination.path, False)
            else:
                LOGGER.info(f"[{destination.label}] Copying '{archive.get_archive_path()}' to '{destination.path}'")
                copy2(archive.get_archive_path(), destination.path)

    def _clean_archives(self, archive: Archive) -> None:
        LOGGER.info("Cleaning old archives")
        prefix_name = ".".join(archive.name.split(".")[:-1])
        for dst in archive.destinations:
            files = os.listdir(dst.path) if not dst.remote else list(map(lambda x: x.replace("\n", ""), self.__ssh.execute(f"find '{dst.path}' -type f -maxdepth 1")[1]))
            files = filter(lambda x: os.path.isfile(os.path.join(dst.path, x)), files) if not dst.remote else map(lambda x: os.path.relpath(x, dst.path), files)
            files = list(filter(lambda x: x.startswith(prefix_name), files))

            files.sort(reverse=True)
            LOGGER.debug(f"[{dst.label}] Files found: {files}")
            keep = dst.versions
            for file in files:
                file_path = os.path.join(dst.path, file)
                if keep == 0 and not dst.remote:
                    os.remove(file_path)
                    LOGGER.info(f"[{dst.label}] File removed: {file}")
                elif keep == 0 and dst.remote:
                    self.__ssh.execute(f"rm '{file_path}'")
                    LOGGER.info(f"[{dst.label}] File removed: {file}")
                else:
                    keep -= 1

    # noinspection PyMethodMayBeStatic
    def _delete_archive(self, archive: Archive) -> None:
        LOGGER.debug("Deleting local archive")
        archive_path = archive.get_archive_path()
        if os.path.isfile(archive_path):
            os.remove(archive_path)
            LOGGER.info(f"Local archive deleted: {archive_path}")
