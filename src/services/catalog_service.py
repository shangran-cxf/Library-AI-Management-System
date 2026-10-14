"""CatalogService：图书标题与馆藏副本维护、查询。"""
from ..domain.enums import ItemStatus, ItemType
from ..domain.models import BookTitle, LibraryItem
from ..exceptions import BusinessRuleError, DuplicateError, NotFoundError, ValidationParamError
from ..repositories import (
    BookTitleRepository,
    LibraryItemRepository,
    ReservationRepository,
)
from ..security import require_admin


class CatalogService:
    def __init__(self, session):
        self.session = session
        self.title_repo = BookTitleRepository(session)
        self.item_repo = LibraryItemRepository(session)
        self.res_repo = ReservationRepository(session)

    def _title_dict(self, title: BookTitle) -> dict:
        return {
            "title_id": title.title_id,
            "title": title.title,
            "author": title.author,
            "isbn": title.isbn,
            "publisher": title.publisher,
            "category": title.category,
            "item_type": title.item_type,
            "available_count": self.item_repo.count_available(title.title_id),
        }

    def search(self, keyword: str | None, category: str | None) -> list:
        return [self._title_dict(t) for t in self.title_repo.search(keyword, category)]

    def add_title(self, req, admin_id: int) -> dict:
        require_admin(self.session, admin_id)
        try:
            item_type = ItemType(req.item_type).value
        except ValueError:
            raise ValidationParamError("借出物类型非法")
        if self.title_repo.get_by_isbn(req.isbn) is not None:
            raise DuplicateError("ISBN 重复")

        title = BookTitle(
            title=req.title,
            author=req.author,
            isbn=req.isbn,
            publisher=req.publisher,
            category=req.category,
            item_type=item_type,
        )
        self.title_repo.save(title)
        data = self._title_dict(title)
        self.session.commit()
        return data

    def delete_title(self, title_id: int, admin_id: int) -> dict:
        require_admin(self.session, admin_id)
        title = self.title_repo.get_by_id(title_id)
        if title is None:
            raise NotFoundError("图书标题不存在")

        for item in self.item_repo.list_by_title(title_id):
            if item.status in (ItemStatus.BORROWED.value, ItemStatus.RESERVED.value):
                raise BusinessRuleError("存在借出或预约中的副本，无法删除")
        if self.res_repo.count_active_by_title(title_id) > 0:
            raise BusinessRuleError("存在有效预约，无法删除")

        self.title_repo.delete(title)
        self.session.commit()
        return {"title_id": title_id, "deleted": True}

    def add_item(self, req, admin_id: int) -> dict:
        require_admin(self.session, admin_id)
        title = self.title_repo.get_by_id(req.title_id)
        if title is None:
            raise NotFoundError("图书标题不存在")
        if self.item_repo.get_by_barcode(req.barcode) is not None:
            raise DuplicateError("条码重复")

        item = LibraryItem(
            barcode=req.barcode,
            title_id=title.title_id,
            item_type=title.item_type,
            status=ItemStatus.AVAILABLE.value,
            location=req.location,
        )
        self.item_repo.save(item)
        data = {
            "item_id": item.item_id,
            "barcode": item.barcode,
            "title_id": item.title_id,
            "item_type": item.item_type,
            "status": item.status,
            "location": item.location,
        }
        self.session.commit()
        return data

    def delete_item(self, item_id: int, admin_id: int) -> dict:
        require_admin(self.session, admin_id)
        item = self.item_repo.get_by_id(item_id)
        if item is None:
            raise NotFoundError("馆藏副本不存在")
        if item.status != ItemStatus.AVAILABLE.value:
            raise BusinessRuleError("副本不可删除")

        self.item_repo.delete(item)
        self.session.commit()
        return {"item_id": item_id, "deleted": True}
