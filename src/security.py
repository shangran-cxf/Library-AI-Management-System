"""权限校验：图书管理员与系统管理员角色区分。"""
from .exceptions import PermissionDeniedError
from .repositories import LibrarianRepository, SystemAdminRepository


def require_librarian(session, librarian_id) -> None:
    if librarian_id is None or LibrarianRepository(session).get_by_id(librarian_id) is None:
        raise PermissionDeniedError("无权限执行该操作")


def require_admin(session, admin_id) -> None:
    if admin_id is None or SystemAdminRepository(session).get_by_id(admin_id) is None:
        raise PermissionDeniedError("无权限执行该操作")
