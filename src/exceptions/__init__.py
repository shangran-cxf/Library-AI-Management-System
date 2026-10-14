"""自定义异常层次：区分业务错误、权限错误与系统异常。"""


class LibraryError(Exception):
    """业务异常基类，携带 code 与 message。"""

    code = 400

    def __init__(self, message: str = "业务错误"):
        self.message = message
        super().__init__(message)


class ValidationParamError(LibraryError):
    """参数非法。"""

    code = 400


class NotFoundError(LibraryError):
    """资源不存在。"""

    code = 404


class BusinessRuleError(LibraryError):
    """违反业务规则。"""

    code = 400


class CardInvalidError(BusinessRuleError):
    """借阅证不存在或已失效。"""


class BorrowLimitExceededError(BusinessRuleError):
    """超过最大借阅数量。"""


class OverdueBooksError(BusinessRuleError):
    """存在超期未还图书。"""


class ItemNotAvailableError(BusinessRuleError):
    """副本不存在或不可借。"""


class DuplicateError(BusinessRuleError):
    """唯一性冲突（账号 / ISBN / 条码 / 重复预约）。"""


class PermissionDeniedError(LibraryError):
    """越权操作。"""

    code = 403


__all__ = [
    "LibraryError",
    "ValidationParamError",
    "NotFoundError",
    "BusinessRuleError",
    "CardInvalidError",
    "BorrowLimitExceededError",
    "OverdueBooksError",
    "ItemNotAvailableError",
    "DuplicateError",
    "PermissionDeniedError",
]
