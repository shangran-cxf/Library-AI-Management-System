"""AdminService：图书管理员账号维护。"""
from ..domain.models import Librarian
from ..exceptions import DuplicateError, NotFoundError
from ..repositories import LibrarianRepository
from ..security import require_admin


class AdminService:
    def __init__(self, session):
        self.session = session
        self.lib_repo = LibrarianRepository(session)

    def add_librarian(self, req) -> dict:
        require_admin(self.session, req.admin_id)
        if self.lib_repo.get_by_account(req.account) is not None:
            raise DuplicateError("账号已存在")

        librarian = Librarian(name=req.name, account=req.account, password=req.password)
        self.lib_repo.save(librarian)
        data = {
            "librarian_id": librarian.librarian_id,
            "name": librarian.name,
            "account": librarian.account,
        }
        self.session.commit()
        return data

    def delete_librarian(self, librarian_id: int, admin_id: int) -> dict:
        require_admin(self.session, admin_id)
        librarian = self.lib_repo.get_by_id(librarian_id)
        if librarian is None:
            raise NotFoundError("图书管理员不存在")
        self.lib_repo.delete(librarian)
        self.session.commit()
        return {"librarian_id": librarian_id, "deleted": True}
