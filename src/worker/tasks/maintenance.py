import logging
import os
import time

from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

DATA_DIR = "data"
MAX_AGE_SECONDS = 3600


@celery_app.task(name="src.worker.tasks.maintenance.cleanup_temp_files")
def cleanup_temp_files() -> dict:
    removed = 0
    now = time.time()

    if not os.path.exists(DATA_DIR):
        return {"removed": 0}

    for root, _dirs, files in os.walk(DATA_DIR):
        for filename in files:
            path = os.path.join(root, filename)
            try:
                if now - os.path.getmtime(path) > MAX_AGE_SECONDS:
                    os.remove(path)
                    removed += 1
            except OSError as exc:
                logger.warning("Failed to remove %s: %s", path, exc)

    logger.info("Cleanup removed %d stale files", removed)
    return {"removed": removed}
