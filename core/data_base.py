# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------
import json
import sqlite3 as sql
from dataclasses import asdict

from core import settings
from core.models import ApkInfo


# -------------------------------------------------------------------------------
# -- Функции
# -------------------------------------------------------------------------------
def init_db(conn):
    """Создаёт таблицы базы данных."""

    query = """
    CREATE TABLE IF NOT EXISTS apk_files (
        apk_files_sha256 TEXT PRIMARY KEY,
        apk_cert_sha256 TEXT NOT NULL,
        apk_time TIMESTAMP NOT NULL,
        apk_size INTEGER NOT NULL,
        apk_arches TEXT NOT NULL,
        apk_file_names TEXT NOT NULL,
        app_name TEXT NOT NULL,
        app_package TEXT NOT NULL,
        app_version TEXT NOT NULL,
        app_min_sdk TEXT,
        app_target_sdk TEXT,
        app_max_sdk TEXT,
        target_version TEXT,
        target_edition TEXT,
        is_orig_cert BOOLEAN
    )
    """
    if conn:
        conn.execute(query)
    else:
        with sql.connect(settings.DATABASE_PATH) as connection:
            connection.execute(query)


def check_db(sha256: str, conn) -> bool:
    """Проверяет наличие APK в базе данных SQLite по sha256."""

    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM apk_files WHERE apk_files_sha256 = ?", (sha256,))
    return cursor.fetchone() is not None


def read_db(conn, **kwargs):
    """
    Считывает записи об APK по заданным параметрам.
    Если параметры не переданы, вернет все записи.
    """
    cursor = conn.cursor()

    # Базовая часть запроса (порядок колонок сохранен[cite: 6])
    query = """
        SELECT apk_files_sha256, apk_cert_sha256, apk_time, apk_size, apk_arches, apk_file_names,
               app_name, app_package, app_version, app_min_sdk, app_target_sdk, app_max_sdk,
               target_version, target_edition,
               is_orig_cert
        FROM apk_files
    """

    parameters = []

    # Если переданы аргументы для фильтрации, добавляем блок WHERE
    if kwargs:
        conditions = []
        for column, value in kwargs.items():
            # Формируем безопасный запрос для SQLite
            conditions.append(f"{column} = ?")
            parameters.append(value)

        # Склеиваем условия через AND
        query += " WHERE " + " AND ".join(conditions)

    # Выполняем запрос с кортежем параметров
    cursor.execute(query, tuple(parameters))
    rows = cursor.fetchall()

    # Собираем результаты в список объектов ApkInfo
    results = []
    for row in rows:
        results.append(ApkInfo(
            apk_files_sha256=row[0],
            apk_cert_sha256=row[1],
            apk_time=row[2],
            apk_size=row[3],
            apk_arches=json.loads(row[4]),
            apk_file_names=json.loads(row[5]),
            app_name=row[6],
            app_package=row[7],
            app_version=row[8],
            app_min_sdk=row[9],
            app_target_sdk=row[10],
            app_max_sdk=row[11],
            target_version=row[12],
            target_edition=row[13],
            is_orig_cert=row[14]
        ))

    return results


def write_db(info, conn):
    """
    Функция записывает информацию о APK в
    базу данных.
    """

    data_dict = asdict(info)
    data_dict["apk_arches"] = json.dumps(data_dict["apk_arches"])
    data_dict["apk_file_names"] = json.dumps(data_dict["apk_file_names"])

    conn.execute("""
    INSERT OR REPLACE INTO apk_files (
        apk_files_sha256, apk_cert_sha256, apk_time, apk_size, apk_arches, apk_file_names,
        app_name, app_package, app_version, app_min_sdk, app_target_sdk, app_max_sdk,
        target_version, target_edition,
        is_orig_cert
    ) VALUES (
        :apk_files_sha256, :apk_cert_sha256, :apk_time, :apk_size, :apk_arches, :apk_file_names,
        :app_name, :app_package, :app_version, :app_min_sdk, :app_target_sdk, :app_max_sdk,
        :target_version, :target_edition,
        :is_orig_cert
    )
    """, data_dict)
    conn.commit()


# Пока пусть будет такая топорная функция для обновления только одного атрибута
def add_db(sha256: str, conn, apk_file_names: str):
    """
    Добавляет имя файла в список apk_file_names для записи с указанным sha256,
    если такого имени там ещё нет.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT apk_file_names FROM apk_files WHERE apk_files_sha256 = ?", (sha256,))
    row = cursor.fetchone()

    if row is None:
        return

    # Загружаем существующие имена (или инициализируем пустой список, если поле пустое)
    current_names = json.loads(row[0]) if row[0] else []

    # Добавляем новое имя только при его отсутствии
    if apk_file_names not in current_names:
        current_names.append(apk_file_names)
        cursor.execute(
            "UPDATE apk_files SET apk_file_names = ? WHERE apk_files_sha256 = ?",
            (json.dumps(current_names), sha256)
        )
        conn.commit()