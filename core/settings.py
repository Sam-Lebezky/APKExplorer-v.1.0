# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------

from pathlib import Path


# -------------------------------------------------------------------------------
# -- Пути
# -------------------------------------------------------------------------------

# Корень проекта (поднимаемся на 2 уровня вверх от config/settings.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Служебные пути
CONFIG_DIR = BASE_DIR / "config"
UTILS_DIR = BASE_DIR / "utils"

DATABASE_PATH = CONFIG_DIR / "data_base.db"
LICENSES_PATH = CONFIG_DIR / "licenses.json"

# Пути к файлам данных и внешним утилитам
LUA_DECOMPILER_UTIL = r"D:\Programs\decompiler"
CORONA_ARCHIVER_UTIL = r"D:\Programs\Corona_Archiver\corona-archiver-master\corona_archiver.py"
KEYTOOL_UTIL = r"D:\Programs\JDK\jdk-17.0.16+8\bin\keytool.exe"

ARCHIVE_DIR = r"D:\Media\TEST ARCHIVE" # Архив АПК для сортировки и анализа
SORT_DIR = r"D:\Media\04. Games\Day R\Sort APK" # Отсортированный архив АПК

DECOMPILE_LUA_DIR = r"D:\Programs\decompiler"


# -------------------------------------------------------------------------------
# -- Проверки
# -------------------------------------------------------------------------------

if not Path(LUA_DECOMPILER_UTIL).exists():
    print("Декомпилятор Lua не найден")
elif not Path(CORONA_ARCHIVER_UTIL).exists():
    print("Corona Archiver не найден")
elif not Path(KEYTOOL_UTIL).exists():
    print("keytool.exe не найден")
elif not Path(ARCHIVE_DIR).exists():
    print("Папка с APK не найдена")

