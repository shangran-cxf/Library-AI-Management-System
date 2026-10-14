"""馆藏持久化：图书标题与馆藏副本。"""
from ..domain.enums import ItemStatus
from ..domain.models import BookTitle, LibraryItem


class BookTitleRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, title_id: int):
        return self.session.get(BookTitle, title_id)

    def get_by_isbn(self, isbn: str):
        return self.session.query(BookTitle).filter_by(isbn=isbn).first()

    def search(self, keyword: str | None, category: str | None):
        query = self.session.query(BookTitle)
        if keyword:
            like = f"%{keyword}%"
            query = query.filter(
                (BookTitle.title.like(like))
                | (BookTitle.author.like(like))
                | (BookTitle.isbn.like(like))
            )
        if category:
            query = query.filter(BookTitle.category == category)
        return query.all()

    def save(self, title: BookTitle) -> BookTitle:
        self.session.add(title)
        self.session.flush()
        return title

    def delete(self, title: BookTitle) -> None:
        self.session.delete(title)
        self.session.flush()


class LibraryItemRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, item_id: int):
        return self.session.get(LibraryItem, item_id)

    def get_by_barcode(self, barcode: str):
        return self.session.query(LibraryItem).filter_by(barcode=barcode).first()

    def list_by_title(self, title_id: int):
        return self.session.query(LibraryItem).filter_by(title_id=title_id).all()

    def count_available(self, title_id: int) -> int:
        return (
            self.session.query(LibraryItem)
            .filter_by(title_id=title_id, status=ItemStatus.AVAILABLE.value)
            .count()
        )

    def save(self, item: LibraryItem) -> LibraryItem:
        self.session.add(item)
        self.session.flush()
        return item

    def delete(self, item: LibraryItem) -> None:
        self.session.delete(item)
        self.session.flush()
