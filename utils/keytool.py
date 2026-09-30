# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------

import os
import re
import zipfile
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union
from core import settings


# -------------------------------------------------------------------------------
# -- Функции
# -------------------------------------------------------------------------------

def get_apk_cert_sha256(apk_path: Union[str, Path]) -> Optional[str]:
    """
    Извлекает отпечаток сертификата SHA-256 из APK файла.
    Возвращает строку вида '85:6C:D1:83:...' или None в случае ошибки/отсутствия подписи.
    """
    apk_file_path = Path(apk_path)  # Путь к APK
    temp_rsa_path = None

    try:
        # 1. Извлекаем .RSA файл подписи из архива
        with zipfile.ZipFile(apk_file_path, 'r') as apk_archive:
            rsa_filename = None
            for file_info in apk_archive.infolist():
                if file_info.filename.startswith("META-INF/") and file_info.filename.endswith((".RSA", ".DSA", ".EC")):
                    rsa_filename = file_info.filename
                    break

            if not rsa_filename:
                return None

            rsa_file_data = apk_archive.read(rsa_filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".RSA") as temp_rsa_file:
                temp_rsa_file.write(rsa_file_data)
                temp_rsa_path = temp_rsa_file.name

        # 2. Вызываем keytool
        command_result = subprocess.run(
            [settings.KEYTOOL_UTIL, "-printcert", "-file", temp_rsa_path],
            capture_output=True,
            text=True,
            check=True
        )

        output_text = command_result.stdout

        # 3. Ищем SHA256 с помощью регулярного выражения
        # Формат вывода keytool обычно: "SHA256: 85:6C:D1:..." или "SHA-256: 85:6C:D1:..."
        match = re.search(r"SHA-?256:\s*([0-9A-FA-f:]+)", output_text)
        if match:
            return match.group(1).strip()

        return None

    # Перехватываем любые ошибки (сбои распаковки, отсутствие прав, ошибки вызова keytool)[cite: 1]
    except Exception as error:
        print(f"Ошибка при получении сертификата для {apk_file_path.name}: {error}")
        return None

    finally:
        if temp_rsa_path and os.path.exists(temp_rsa_path):
            os.remove(temp_rsa_path)