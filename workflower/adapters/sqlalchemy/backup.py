import logging
import sqlite3
import traceback

logger = logging.getLogger("workflower.adapters.sqlalchemy.backup")


def dump_sqlite(sqlite_path: str, dump_path: str) -> None:
    """
    Backup sqlite database
    """
    logger.info(f"Dumping database: {dump_path}")
    if "sqlite:///" in sqlite_path:
        sqlite_path = sqlite_path[10:]
    con = sqlite3.connect(sqlite_path)
    try:
        with open(dump_path, "w") as f:
            for line in con.iterdump():
                f.write("%s\n" % line)
    except Exception:
        logger.error(f"Error: {traceback.print_exc()}")
    finally:
        con.close()


def _progress(status, remaining, total):
    logger.info(f"Database backup: {total-remaining} of {total} pages...")


def backup_sqlite(
    sqlite_origin_path: str, sqlite_destination_path: str
) -> None:
    """
    Sqlite backup
    """
    logger.info(
        f"Backing up database: {sqlite_origin_path} to "
        f"{sqlite_destination_path}"
    )
    if "sqlite:///" in sqlite_origin_path:
        sqlite_origin_path = sqlite_origin_path[10:]
    if "sqlite:///" in sqlite_destination_path:
        sqlite_destination_path = sqlite_destination_path[10:]
    try:
        con = sqlite3.connect(sqlite_origin_path)
        bck = sqlite3.connect(sqlite_destination_path)
        with bck:
            con.backup(bck, pages=1, sleep=0.25, progress=_progress)
        bck.close()
        con.close()
    except Exception:
        logger.error(f"Error: {traceback.print_exc()}")
    finally:
        con.close()
