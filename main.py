from pathlib import Path
from loguru import logger
import sqlite3 as sql
import time

from core import settings
from core.analyzer import get_apk_files_sha256, get_apk_info
from core.prints import print_result
from core.data_base import init_db, get_apk, write_db, add_db
from games.day_r import run_sort
logger.remove()

def main():
    """
    Вход в программу. Начало процесса.
    """

    # Единая сессия подключения на весь цикл обработки
    with sql.connect(settings.DATABASE_PATH) as conn:
        init_db(conn)

        for i, apk in enumerate(Path(settings.ARCHIVE_DIR).rglob("*.apk"), start=1):
            '''if i > 2:
                break'''

            print(f"АПК №{i}")

            sha256 = get_apk_files_sha256(apk)
            info = get_apk(sha256, conn)

            if info is not None:
                print(f"{i}. --- Старый APK ---")
            else:
                info = get_apk_info(apk, sha256)
                write_db(info, conn)
                print(f"{i}. --- Новый APK ---")

            #регистрируем текущее имя, тиггер  обновит главную таблицу, если имя новое.
            add_db(sha256, conn, apk.stem, apk_file_path=str(apk))
            # Перечитываем, чтобы получить актуальный apk_file_names после триггера.
            info = get_apk(sha256, conn)

            print_result(info)
            run_sort(apk, info)
            print("Перерыв 2 секунды...")
            time.sleep(2)


if __name__ == '__main__':
    main()
