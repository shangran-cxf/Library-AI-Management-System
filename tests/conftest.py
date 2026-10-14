"""pytest 公共 fixture：内存 SQLite + TestClient + 预置数据。"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, _seed_defaults, get_db
from src.domain.enums import CardStatus, ItemStatus, ItemType, ReaderType
from src.domain.models import (
    BookTitle,
    BorrowCard,
    Librarian,
    LibraryItem,
    Reader,
    SystemAdmin,
)
from src.main import app


def _sessionmaker(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    _seed_defaults(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def db(engine):
    session = _sessionmaker(engine)()
    yield session
    session.close()


@pytest.fixture()
def client(engine):
    def override():
        session = _sessionmaker(engine)()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def seed(db):
    """预置系统管理员、图书管理员、读者、借阅证、图书标题与副本。"""
    # 显式指定管理员 ID，避免与读者表自增 ID 冲突（角色隔离依赖 ID 不重叠）
    admin = SystemAdmin(admin_id=100, name="系统管理员", account="admin", password="admin123")
    librarian = Librarian(librarian_id=200, name="图书管理员", account="lib", password="lib123")
    reader = Reader(
        name="张三",
        department="计算机",
        reader_type=ReaderType.UNDERGRADUATE.value,
        account="zhangsan",
        password="123456",
    )
    reader2 = Reader(
        name="李四",
        department="电子",
        reader_type=ReaderType.JUNIOR.value,
        account="lisi",
        password="123456",
    )
    teacher = Reader(
        name="王老师",
        department="计算机",
        reader_type=ReaderType.TEACHER.value,
        account="teacher",
        password="123456",
    )
    db.add_all([admin, librarian, reader, reader2, teacher])
    db.flush()

    card = BorrowCard(
        card_no="CARD2026000001",
        reader_id=reader.reader_id,
        status=CardStatus.ACTIVE.value,
    )
    db.add(card)

    title = BookTitle(
        title="数据结构",
        author="严蔚敏",
        isbn="9787302000001",
        category="计算机",
        item_type=ItemType.CHINESE_BOOK.value,
    )
    db.add(title)
    db.flush()

    item1 = LibraryItem(
        barcode="BC0001",
        title_id=title.title_id,
        item_type=title.item_type,
        status=ItemStatus.AVAILABLE.value,
    )
    item2 = LibraryItem(
        barcode="BC0002",
        title_id=title.title_id,
        item_type=title.item_type,
        status=ItemStatus.AVAILABLE.value,
    )
    db.add_all([item1, item2])
    db.commit()

    return {
        "admin_id": admin.admin_id,
        "librarian_id": librarian.librarian_id,
        "reader_id": reader.reader_id,
        "reader2_id": reader2.reader_id,
        "teacher_id": teacher.reader_id,
        "card_no": card.card_no,
        "title_id": title.title_id,
        "isbn": title.isbn,
        "barcodes": [item1.barcode, item2.barcode],
        "item_ids": [item1.item_id, item2.item_id],
    }
