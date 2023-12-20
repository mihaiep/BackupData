import json

from core.backup import BackupExecutor
from core.resolvers import JsonResolver
from misc.utils import LOGGER

if __name__ == '__main__':
    status_success = False

    try:
        json_file_path = "config.json"
        cfg = JsonResolver(json_file_path)

        backup_executor = BackupExecutor(cfg.force, cfg.require_ssh, cfg.ssh)
        backup_executor.execute(cfg.backups)
        cfg.update_last_run_date()

        open(json_file_path, 'w').writelines(json.dumps(cfg.to_json(), indent='\t'))
        status_success = True
    finally:
        LOGGER.end_execution()
