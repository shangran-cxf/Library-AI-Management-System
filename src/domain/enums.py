"""值对象：业务枚举（值等于名称，便于数据库以字符串存储）。"""
from enum import Enum


class ReaderType(str, Enum):
    JUNIOR = "JUNIOR"
    UNDERGRADUATE = "UNDERGRADUATE"
    GRADUATE = "GRADUATE"
    DOCTOR = "DOCTOR"
    TEACHER = "TEACHER"


class ItemType(str, Enum):
    CHINESE_BOOK = "CHINESE_BOOK"
    FOREIGN_BOOK = "FOREIGN_BOOK"
    CHINESE_MAGAZINE = "CHINESE_MAGAZINE"
    FOREIGN_MAGAZINE = "FOREIGN_MAGAZINE"
    THESIS = "THESIS"


class LoanStatus(str, Enum):
    BORROWING = "BORROWING"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


class ReservationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class CardStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    REMOVED = "REMOVED"


class FineStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"


def as_value(enum_cls, value):
    """将字符串校验为指定枚举，非法则抛 ValueError。"""
    return enum_cls(value).value
