
import json
import sqlite3 as sql
from dataclasses import asdict
from typing import Optional

from core import settings
from core.models import ApkInfo


# Порядок колонок
_COLUMNS = """
    apk_files_sha256, apk_cert_sha256, apk_time, apk_size, apk_arches, apk_file_names,
    app_name, app_package, app_version, app_min_sdk, app_target_sdk, app_max_sdk,
    target_version, target_edition, is_orig_cert
"""


def _row_to_apk_info(row) -> ApkInfo:#pаспаковывает строку из БД в объект ApkInfo
    
    return ApkInfo(
        apk_files_sha256=row[0],
        apk_cert_sha256=row[1],
        apk_time=row[2],
        apk_size=row[3],
        apk_arches=json.loads(row[4]),
        apk_file_names=json.loads(row[5]) if row[5] else [],
        app_name=row[6],
        app_package=row[7],
        app_version=row[8],
        app_min_sdk=row[9],
        app_target_sdk=row[10],
        app_max_sdk=row[11],
        target_version=row[12],
        target_edition=row[13],
        is_orig_cert=row[14],
    )


def init_db(conn):#создание таблиц, триггеров, индексов
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS apk_files (
        apk_files_sha256 TEXT PRIMARY KEY,
        apk_cert_sha256 TEXT NOT NULL,
        apk_time TIMESTAMP NOT NULL,
        apk_size INTEGER NOT NULL,
        apk_arches TEXT NOT NULL,
        apk_file_names TEXT NOT NULL DEFAULT '[]',
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
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS apk_files_duplicates (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        apk_files_sha256  TEXT NOT NULL,
        apk_file_name     TEXT NOT NULL,
        apk_file_path     TEXT,
        discovered_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(apk_files_sha256, apk_file_name),
        FOREIGN KEY (apk_files_sha256) REFERENCES apk_files(apk_files_sha256)
            ON DELETE CASCADE
    )
    """)

    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_duplicates_sha256
        ON apk_files_duplicates(apk_files_sha256)
    """)

    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_duplicates_ai
    AFTER INSERT ON apk_files_duplicates
    BEGIN
        UPDATE apk_files
        SET apk_file_names = (
            SELECT json_group_array(apk_file_name)
            FROM (
                SELECT apk_file_name FROM apk_files_duplicates
                WHERE apk_files_sha256 = NEW.apk_files_sha256
                ORDER BY id
            )
        )
        WHERE apk_files_sha256 = NEW.apk_files_sha256;
    END
    """)

    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_duplicates_ad
    AFTER DELETE ON apk_files_duplicates
    BEGIN
        UPDATE apk_files
        SET apk_file_names = COALESCE(
            (
                SELECT json_group_array(apk_file_name)
                FROM (
                    SELECT apk_file_name FROM apk_files_duplicates
                    WHERE apk_files_sha256 = OLD.apk_files_sha256
                    ORDER BY id
                )
            ),
            '[]'
        )
        WHERE apk_files_sha256 = OLD.apk_files_sha256;
    END
    """)

    conn.commit()


def get_apk(sha256: str, conn) -> Optional[ApkInfo]:#возвращает ApkInfo по sha256 или None
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT {_COLUMNS} FROM apk_files WHERE apk_files_sha256 = ?",
        (sha256,),
    )
    row = cursor.fetchone()
    return _row_to_apk_info(row) if row is not None else None


def read_db(conn, **kwargs) -> list[ApkInfo]:#считывает записи об APK по заданным параметрам
    
    cursor = conn.cursor()
    query = f"SELECT {_COLUMNS} FROM apk_files"
    parameters = []

    if kwargs:
        conditions = [f"{column} = ?" for column in kwargs]
        query += " WHERE " + " AND ".join(conditions)
        parameters = list(kwargs.values())

    cursor.execute(query, tuple(parameters))
    return [_row_to_apk_info(row) for row in cursor.fetchall()]


def write_db(info: ApkInfo, conn):#Записывает основную информацию об APK
    
    data = asdict(info)
    data["apk_arches"] = json.dumps(data["apk_arches"])

    conn.execute("""
    INSERT INTO apk_files (
        apk_files_sha256, apk_cert_sha256, apk_time, apk_size, apk_arches,
        app_name, app_package, app_version, app_min_sdk, app_target_sdk, app_max_sdk,
        target_version, target_edition, is_orig_cert
    ) VALUES (
        :apk_files_sha256, :apk_cert_sha256, :apk_time, :apk_size, :apk_arches,
        :app_name, :app_package, :app_version, :app_min_sdk, :app_target_sdk, :app_max_sdk,
        :target_version, :target_edition, :is_orig_cert
    )
    ON CONFLICT(apk_files_sha256) DO UPDATE SET
        apk_cert_sha256 = excluded.apk_cert_sha256,
        apk_time        = excluded.apk_time,
        apk_size        = excluded.apk_size,
        apk_arches      = excluded.apk_arches,
        app_name        = excluded.app_name,
        app_package     = excluded.app_package,
        app_version     = excluded.app_version,
        app_min_sdk     = excluded.app_min_sdk,
        app_target_sdk  = excluded.app_target_sdk,
        app_max_sdk     = excluded.app_max_sdk,
        target_version  = excluded.target_version,
        target_edition  = excluded.target_edition,
        is_orig_cert    = excluded.is_orig_cert
    """, data)
    conn.commit()


def add_db(sha256: str, conn, apk_file_name: str, apk_file_path: Optional[str] = None):#Регистрирует имя файла как дубль
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO apk_files_duplicates
            (apk_files_sha256, apk_file_name, apk_file_path)
        VALUES (?, ?, ?)
    """, (sha256, apk_file_name, apk_file_path))
    conn.commit()


def get_duplicates(sha256: str, conn) -> list[dict]: #Возвращает все записи дублей для APK
   
    cursor = conn.cursor()
    cursor.execute("""
        SELECT apk_file_name, apk_file_path, discovered_at
        FROM apk_files_duplicates
        WHERE apk_files_sha256 = ?
        ORDER BY id
    """, (sha256,))
    return [
        {"apk_file_name": r[0], "apk_file_path": r[1], "discovered_at": r[2]}
        for r in cursor.fetchall()
    ]