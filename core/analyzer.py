# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------

import hashlib, zipfile
import os
from androguard.core.apk import APK
from datetime import datetime
from pathlib import Path

from core import settings
from core.models import ApkInfo
from core.prints import print_android
from utils.keytool import get_apk_cert_sha256
from utils.solar2d import run_extract_car, run_unpack_car, run_decompile_lu, run_clear_decompiler
from games.day_r import get_edition, get_version


# -------------------------------------------------------------------------------
# -- Функции
# -------------------------------------------------------------------------------

def get_apk_files_sha256(apk_path: str) -> str:
    """
    Функция превращает содержимое APK в хеш и возвращает как строку.
    """
    hasher = hashlib.sha256()  # Выбираем кодировку - sha256
    with open(apk_path, "rb") as f:  # Читаем APK по байтам
        # По очереди шифруем каждые 64 кб
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()  # Возвращаем хеш


def get_apk_build_date(apk_path) -> str:
    """
    Функция определяет дату сборки APK. Возвращает строку с датой.
    """
    # Открываем APK
    with zipfile.ZipFile(apk_path, 'r') as zip_file:
        valid_dates = []  # Список дат файлов # WARNING: Мб использовать set()?
        for file_info in zip_file.infolist():  # Проходимся циклом по каждому файлу
            # Игнорируем зафиксированные даты Android SDK (2008 и ранее)
            # Если дата файла больше 2008, то запоминаем её
            if file_info.date_time[0] > 2008:
                valid_dates.append(datetime(*file_info.date_time))

        # Если в списке есть даты, то возвращаем самую новую
        if valid_dates:
            return max(valid_dates).strftime("%Y-%m-%d %H:%M:%S")

        # Если в списке нет дат старше 2008 года, то возвращаем заглушку
        return "Дата сброшена"


def get_apk_architectures(apk_path) -> list:
    """
    Функция определяет процессорные архитектуры, которые
    поддерживает APK. Возвращает список строк, где
    каждая строка - имя архитектуры.
    """
    arches = set()  # Создаём пустое множество: {}
    with zipfile.ZipFile(apk_path, 'r') as zip_file:
        for file_info in zip_file.infolist():
            # Все нативные библиотеки (.so) находятся в каталоге lib/<архитектура>/
            if file_info.filename.startswith("lib/") and file_info.filename.endswith(".so"):
                parts = file_info.filename.split('/')  # Разделяем путь к объекту на части
                if len(parts) > 2:  # Включаем только объекты с длиной имени более 2-х символов
                    arches.add(parts[1])  # Извлекаем имя архитектуры (например, arm64-v8a)

    # Возвращаем список строк. Если список пуст, то заглушку
    return list(arches) if arches else ["Универсальный (no native libs)"]


def get_apk_info(apk_path: str | Path, apk_sha256: str) -> ApkInfo:
    """
    Определяет всю метаинформацию об APK-файле.
    """
    path = Path(apk_path)
    apk_obj = APK(path)

    # 1. Свойства файла (уровень APK/диска)
    apk_file_size = path.stat().st_size
    apk_build_time = get_apk_build_date(path)
    apk_architectures = get_apk_architectures(path)
    apk_file_names = [path.stem]
    apk_cert_hash = get_apk_cert_sha256(path)

    # 2. Свойства приложения (уровень AndroidManifest.xml)
    app_name = apk_obj.get_app_name()
    app_package = apk_obj.get_package()
    app_version = apk_obj.get_androidversion_name()
    app_min_sdk = print_android(apk_obj.get_min_sdk_version())
    app_target_sdk = print_android(apk_obj.get_target_sdk_version())
    app_max_sdk = print_android(apk_obj.get_max_sdk_version())

    # 3. Свойства текущего приложения
    if True:
    # if False:
        resource_car = run_extract_car(apk_path)
        run_unpack_car(resource_car, settings.DECOMPILE_LUA_DIR)
        run_decompile_lu()
        os.remove(resource_car)

        # Тут нужно передавать apk_path или нет?
        target_version = get_version()
        target_edition, is_orig_cert = get_edition(apk_cert_hash)

        run_clear_decompiler("input")
        run_clear_decompiler("output")

    # 4. Сборка модели
    return ApkInfo(
        apk_files_sha256=apk_sha256,
        apk_cert_sha256=apk_cert_hash,
        apk_time=apk_build_time,
        apk_size=apk_file_size,
        apk_arches=apk_architectures,
        apk_file_names=apk_file_names,
        app_name=app_name,
        app_package=app_package,
        app_version=app_version,
        app_min_sdk=app_min_sdk,
        app_target_sdk=app_target_sdk,
        app_max_sdk=app_max_sdk,
        target_version=target_version,
        target_edition=target_edition,
        is_orig_cert=is_orig_cert
    )