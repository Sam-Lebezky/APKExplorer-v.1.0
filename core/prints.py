# -------------------------------------------------------------------------------
# -- Функции
# -------------------------------------------------------------------------------

def print_android(sdk_id):
    # Словарь соответствия API Level и версии Android
    android_versions = {
        "1": "1.0 (Base)",
        "2": "1.1 (Banana Bread)",
        "3": "1.5 (Cupcake)",
        "4": "1.6 (Donut)",
        "5": "2.0 (Eclair)",
        "6": "2.0.1 (Eclair)",
        "7": "2.1 (Eclair)",
        "8": "2.2 (Froyo)",
        "9": "2.3 (Gingerbread)",
        "10": "2.3.3 (Gingerbread)",
        "11": "3.0 (Honeycomb)",
        "12": "3.1 (Honeycomb)",
        "13": "3.2 (Honeycomb)",
        "14": "4.0 (Ice Cream Sandwich)",
        "15": "4.0.3 (Ice Cream Sandwich)",
        "16": "4.1 (Jelly Bean)",
        "17": "4.2 (Jelly Bean)",
        "18": "4.3 (Jelly Bean)",
        "19": "4.4 (KitKat)",
        "20": "4.4W (KitKat Wear)",
        "21": "5.0 (Lollipop)",
        "22": "5.1 (Lollipop)",
        "23": "6.0 (Marshmallow)",
        "24": "7.0 (Nougat)",
        "25": "7.1 (Nougat)",
        "26": "8.0 (Oreo)",
        "27": "8.1 (Oreo)",
        "28": "9.0 (Pie)",
        "29": "10.0 (Quince Tart)",
        "30": "11.0 (Red Velvet Cake)",
        "31": "12.0 (Snow Cone)",
        "32": "12L (Snow Cone v2)",
        "33": "13.0 (Tiramisu)",
        "34": "14.0 (Upside Down Cake)",
        "35": "15.0 (Vanilla Ice Cream)",
        "36": "16.0 (Baklava)",
    }

    # .get() вернет понятную версию или сам ID, если его нет в словаре
    android_version = android_versions.get(str(sdk_id), f"API {sdk_id}")
    return android_version


def print_result(info): # Название и положение функции надо будет заменить
    print(f"   Хеш АПК: {info.apk_files_sha256}")
    print(f"   Хеш сертификата: {info.apk_cert_sha256}")
    print(f"   Оригинальность APK: {info.is_orig_cert}")
    print(f"   Дата создания: {info.apk_time}")
    print(f"   Архитектуры APK: {', '.join(info.apk_arches)}")
    print(f"   Имена APK: {', '.join(info.apk_file_names)}")
    print(f"   Размер APK: {info.apk_size // 1024 ** 2} МБ")
    print(f"   Имя приложения: {info.app_name}")
    print(f"   Пакет приложения: {info.app_package}")
    print(f"   Версия приложения: {info.app_version}")
    print(f"   Минимальный Android: {info.app_min_sdk}")
    print(f"   Целевой Android: {info.app_target_sdk}")
    print(f"   Максимальный Android: {info.app_max_sdk}")
    print(f"   Версия игры: {info.target_version}")
    print(f"   Издание: {info.target_edition}")