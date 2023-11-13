import base64
import os.path
import re
from datetime import datetime
from typing import Optional
from melogger import LoggerBuilder, Levels

LOGGER = LoggerBuilder.get_logger("VaultBackup", Levels.INFO, logs_path=os.path.abspath(".."), file_name="vault_backup.log")


class VaultBackupException(Exception):
    pass


def password_decrypt(encrypted_password: str) -> Optional[str]:
    return base64.b64decode(encrypted_password).decode()


def password_encrypt(password: str) -> str:
    return base64.b64encode(password.encode()).decode()


def convert(expected: type, data: any) -> any:
    """Convert JSON element to a primitive"""
    if data is None or expected == type(data):
        return data
    try:
        if expected == int:
            return int(float(str(data)))
        elif expected == float:
            return float(str(data))
        elif expected == str:
            return str(data)
        elif expected == bool:
            data = str(data)
            if data.lower() in ["0", "no", "false"]:
                return False
            if data.lower() in ["1", "yes", "true"]:
                return True
        raise VaultBackupException(f"Operation not supported.")
    except Exception as e:
        raise VaultBackupException(f"Cannot convert '{data}' to {expected} - {e.__str__()}")


def handle_password(value) -> Optional[str]:
    password = convert(str, value)
    if password is None:
        return None
    matches = re.findall(r"^enc(?:rypt)?\((.+)\)$", password)
    if len(matches) == 0:
        password_decrypt(password)
        return password
    return password_encrypt(matches[0])


def handle_timestamp(value) -> datetime:
    value = convert(str, value)
    return datetime(1900, 1, 1) if value is None else datetime.fromisoformat(value)


def not_none(key: str, value: any) -> any:
    if value is None:
        raise VaultBackupException(f"Key '{key}' cannot be None.")
    return value
