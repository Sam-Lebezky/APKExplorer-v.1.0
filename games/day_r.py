# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------

import json
import shutil
from pathlib import Path

from core import settings


# -------------------------------------------------------------------------------
# -- Вспомогательные функции
# -------------------------------------------------------------------------------

def search_string(string, file):
    with open(file, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            if string in line:
                return True
    return None


def search_string_strip(string, file):
    with open(file, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, 1):
            if string in line:
                # Метод split делит строку на две части: всё, что до target, и всё, что после
                after_text = line.split(string)[1]

                # Метод strip() удалит лишние пробелы и переносы строк по краям
                return after_text.strip()
    return None


# -------------------------------------------------------------------------------
# -- Функции анализа
# -------------------------------------------------------------------------------

def get_version():
    # Преобразуем генератор в список найденных файлов
    output_dir = Path(settings.DECOMPILE_LUA_DIR) / "output"

    main_files = list(output_dir.glob("main.lua"))
    config_files = list(output_dir.glob("config.lua"))

    # Берем первый файл из списка, если список не пуст
    file_main = main_files[0] if main_files else None
    file_config = config_files[0] if config_files else None

    if file_main:
        return search_string_strip("CURRENT_VERSION = ", file_main)
    elif file_config:
        return search_string_strip("appVersion = ", file_config)


def get_edition(apk_cert_hash):
    # Сравниваем apk_cert_hash с базой сертификатов
    with open(settings.LICENSES_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)

    apk_hash_clean = str(apk_cert_hash).strip().upper() if apk_cert_hash else ""

    for edition, cert_hash in data.items():

        if cert_hash.strip().upper() == apk_hash_clean:
            return edition, True

    output_dir = Path(settings.DECOMPILE_LUA_DIR) / "output"

    premium_files = list(output_dir.glob("*.premium.lua"))
    main_files = list(output_dir.glob("main.lua"))

    file_main = main_files[0] if main_files else None
    file_premium = premium_files[0] if premium_files else None

    # Теперь безопасно ищем (проверяя, что файлы вообще нашлись)
    premium = False
    if file_premium:
        premium = search_string("p1_0 = YES", file_premium)
    if not premium and file_main:
        premium = search_string("PREMIUM_APK = true", file_main)

    return ("Premium", False) if premium else ("Survival", False)


def run_sort(apk, info):
    edition = info.target_edition # Издание игры (Премиум, Обычная, Бета или Альфа)
    original = "Original" if info.is_orig_cert else "Unoriginal" # Оригинальность APK
    version = None # CURRENT_VERSION

    # Проверяем, можно ли перевести CURRENT_VERSION в вид "1.???"
    # В некоторых версиях CURRENT_VERSION не было, поэтому
    # передаётся None. Также в некоторых версиях, емнип, эта
    # константа равнялась 1.0 (1.000). Но формула перевела бы такой
    # номер в 1.001, тем самым перепутав версию.
    if info.target_version and int(info.target_version) > 1:
        version = str(1 + int(info.target_version) / 1000)

    # Определение нового пути APK
    base_dir = Path(settings.SORT_DIR)
    output_dir = base_dir / f"{original} {edition}" / f"{version or "- "} ({info.app_version})"
    output_dir.mkdir(parents=True, exist_ok=True) # Создание пути

    # Проверяем, нет ли в папке назначения такого же APK
    # target_apk_files - список APK из папки назначения
    # target_apk - APK с которым проверяется сходство
    is_duplicate = False # Флаг, что текущий APK - повторка
    target_apk_files = output_dir.glob("*.apk") # Список APK
    for target_apk in target_apk_files: # Проходимся циклом по всем файлам
        if info.apk_size == target_apk.stat().st_size: # Проверяем сходство по весу
            from core.analyzer import get_apk_files_sha256

            # Проверяем сходство по хешу содержимого
            if info.apk_files_sha256 == get_apk_files_sha256(target_apk):
                is_duplicate = True # Если совпало, активируем флаг
                break

    # Исключение повторных апк
    # Повторки отправляются в отдельную папку
    if not is_duplicate:
        shutil.move(apk, output_dir)
    else:
        # Создаём папку, если её ещё нет
        duplicates_dir = base_dir / "Повторки/"
        duplicates_dir.mkdir(parents=True, exist_ok=True)

        # Проверяем, нет ли повторки с таким же именем
        # Если нет - перетаскиваем файл
        # Если да - просто удаляем (Вообще лучше не удалять, а добавлять (n) в конце имени файла, где n - число)
        target_path = duplicates_dir / apk.name
        if not target_path.is_file():
            shutil.move(apk, duplicates_dir)
        else:
            Path(apk).unlink(missing_ok=False)

