from paramiko.channel import ChannelStderrFile, ChannelFile, ChannelStdinFile
from paramiko.client import SSHClient, AutoAddPolicy
from scp import SCPClient

from core.type import SSHInfo
from misc.utils import LOGGER


class SSHConnection:
    def __init__(self, ssh: SSHInfo):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(ssh.ip, int(ssh.port), ssh.user, ssh.get_password())
        self.scp = SCPClient(self.client.get_transport())

    def execute(self, command: str) -> tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile]:
        LOGGER.debug(f"Executing SSH command: {command}")
        return self.client.exec_command(command)

    def download(self, remote_source: str, local_destination: str, is_dir: bool):
        self.scp.get(remote_source, local_destination, is_dir, True)
        LOGGER.debug("{} '{}' was downloaded to {}".format(f"Directory" if is_dir else "File", remote_source, local_destination))

    def upload(self, local_source: str, remote_destination: str, is_dir: bool):
        self.scp.put(local_source, remote_destination, is_dir, True)
        LOGGER.debug("{} '{}' was uploaded to {}".format(f"Directory" if is_dir else "File", local_source, remote_destination))

    def close(self) -> None:
        self.scp.close()
        self.client.close()
