# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------
from pathlib import Path
from loguru import logger
import sqlite3 as sql
import time

from core import settings
from core.analyzer import get_apk_files_sha256, get_apk_info
from core.prints import print_result
from core.data_base import init_db, check_db, read_db, write_db, add_db
from games.day_r import run_sort
logger.remove()


# -------------------------------------------------------------------------------
# -- Функции
# -------------------------------------------------------------------------------
def main():
    """
    Вход в программу. Начало процесса.
    """

    # Единая сессия подключения на весь цикл обработки
    with sql.connect(settings.DATABASE_PATH) as conn:
        init_db(conn)

        # Проверяем каждый APK из архива по очереди
        for i, apk in enumerate(Path(settings.ARCHIVE_DIR).rglob("*.apk"), start=1):
            if i > 2: # Временная заглушка: берём только первые 5 APK
                break

            print(f"АПК №{str(i)}")

            sha256 = get_apk_files_sha256(apk)  # Хеш APK

            if check_db(sha256, conn):
                add_db(sha256, conn, apk.stem)
                info = read_db(conn, apk_files_sha256=sha256)

                print(f"{i}. --- Старый APK ---")
                print_result(info[0])
                run_sort(apk, info[0])
                print("Перерыв 2 секунды...")
                time.sleep(2)
            else:
                info = get_apk_info(apk, sha256) # Получаем всю информацию о APK
                write_db(info, conn)

                print(f"{i}. --- Новый APK ---")
                print_result(info)
                run_sort(apk, info)
                print("Перерыв 2 секунды...")
                time.sleep(2)


# -------------------------------------------------------------------------------
# -- Вызов
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
