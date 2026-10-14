"""管理员持久化：图书管理员与系统管理员。"""
from ..domain.models import Librarian, SystemAdmin


class LibrarianRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, librarian_id: int):
        return self.session.get(Librarian, librarian_id)

    def get_by_account(self, account: str):
        return self.session.query(Librarian).filter_by(account=account).first()

    def save(self, librarian: Librarian) -> Librarian:
        self.session.add(librarian)
        self.session.flush()
        return librarian

    def delete(self, librarian: Librarian) -> None:
        self.session.delete(librarian)
        self.session.flush()


class SystemAdminRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, admin_id: int):
        return self.session.get(SystemAdmin, admin_id)

    def get_by_account(self, account: str):
        return self.session.query(SystemAdmin).filter_by(account=account).first()

    def save(self, admin: SystemAdmin) -> SystemAdmin:
        self.session.add(admin)
        self.session.flush()
        return admin

    def delete(self, admin: SystemAdmin) -> None:
        self.session.delete(admin)
        self.session.flush()
