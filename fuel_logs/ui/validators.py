import re
from datetime import datetime

DATE_FMT_RU = "%d.%m.%Y"
DATE_FMT_DB = "%Y-%m-%d"
PLATE_RE = re.compile(r"^[АВЕКМНОРСТУХABEKMHOPCTYX]\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$", re.IGNORECASE)
FIO_RE = re.compile(r"^[А-Яа-яЁёA-Za-z\-\s]{5,120}$")


def parse_date_ru_to_db(value: str, field_name: str) -> str:
    value = value.strip()
    try:
        dt = datetime.strptime(value, DATE_FMT_RU)
    except ValueError as e:
        raise ValueError(f"Поле «{field_name}» должно быть в формате ДД.ММ.ГГГГ, например 11.11.2000") from e
    return dt.strftime(DATE_FMT_DB)


def format_date_db_to_ru(value: str) -> str:
    try:
        return datetime.strptime(value, DATE_FMT_DB).strftime(DATE_FMT_RU)
    except Exception:
        return value


def parse_float_ru(value: str, field_name: str, min_value: float | None = 0) -> float:
    raw = value.strip().replace(",", ".")
    if not raw:
        raise ValueError(f"Поле «{field_name}» обязательно")
    try:
        num = float(raw)
    except ValueError as e:
        raise ValueError(f"Поле «{field_name}» должно быть числом") from e
    if min_value is not None and num < min_value:
        raise ValueError(f"Поле «{field_name}» не может быть меньше {min_value}")
    return num


def validate_plate(value: str) -> str:
    plate = value.strip().replace(" ", "").upper()
    if not PLATE_RE.match(plate):
        raise ValueError("Гос. номер должен быть в формате А123ВС77 (или с латинскими аналогами букв)")
    return plate


def validate_fio(value: str) -> str:
    fio = " ".join(value.strip().split())
    if not FIO_RE.match(fio):
        raise ValueError("Введите ФИО кириллицей/латиницей: минимум 5 символов, только буквы, пробел и дефис")
    return fio
