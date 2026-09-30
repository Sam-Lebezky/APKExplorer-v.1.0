# -------------------------------------------------------------------------------
# -- Импорты
# -------------------------------------------------------------------------------
from dataclasses import dataclass
from typing import List, Optional


# -------------------------------------------------------------------------------
# -- Классы
# -------------------------------------------------------------------------------
@dataclass
class ApkInfo:
    apk_files_sha256: str
    apk_cert_sha256: str
    apk_time: str
    apk_size: int
    apk_arches: List[str]
    apk_file_names: List[str]
    app_name: str
    app_package: str
    app_version: str
    app_min_sdk: Optional[str]
    app_target_sdk: Optional[str]
    app_max_sdk: Optional[str]
    target_version: Optional[str]
    target_edition: Optional[str]
    is_orig_cert: bool