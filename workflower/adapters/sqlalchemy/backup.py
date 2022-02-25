import logging
import sqlite3
import traceback

from workflower.adapters.sqlalchemy.setup import engine

logger = logging.getLogger("workflower.adapters.sqlalchemy.backup")


def dump_sqlite(path):
    """
    Backup sqlite database
    """
    logger.info(f"Dumping database: {path}")
    con = engine.raw_connection()
    try:
        with open(path, "w") as f:
            for line in con.iterdump():
                f.write("%s\n" % line)
    except Exception:
        logger.error(f"Error: {traceback.print_exc()}")
    finally:
        con.close()


def progress(status, remaining, total):
    logger.info(f"Database backup: {total-remaining} of {total} pages...")


def backup_sqlite(origin_path, destination_path):
    logger.info(f"Backing up database: {origin_path} to {destination_path}")
    if "sqlite:///" in origin_path:
        origin_path = origin_path[10:]
    if "sqlite:///" in destination_path:
        destination_path = destination_path[10:]
    try:
        con = sqlite3.connect(origin_path)
        bck = sqlite3.connect(destination_path)
        with bck:
            con.backup(bck, pages=1, sleep=0.25, progress=progress)
        bck.close()
        con.close()
    except Exception:
        logger.error(f"Error: {traceback.print_exc()}")
    finally:
        con.close()
