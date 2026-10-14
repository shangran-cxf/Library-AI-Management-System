"""pytest 公共 fixture：内存 SQLite + TestClient + 预置数据。"""
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 让测试可以 import app.* （backend 目录加入 sys.path）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Base, Book, BorrowRecord, User  # noqa: E402
from app.routes import app, get_db  # noqa: E402


def _make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def client(engine):
    SessionTesting = _make_session_factory(engine)

    def override_get_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def seed(engine):
    """预置用户、图书、借阅记录，返回常用 ID。"""
    SessionTesting = _make_session_factory(engine)
    db = SessionTesting()

    reader = User(username="zhangsan", password="123456", role="reader", max_borrow=5)
    other = User(username="lisi", password="123456", role="reader", max_borrow=5)
    db.add_all([reader, other])
    db.flush()

    book = Book(
        title="三体",
        author="刘慈欣",
        isbn="9787536692930",
        category="科幻",
        total_copies=5,
        available_copies=3,
    )
    db.add(book)
    db.flush()

    from datetime import datetime

    borrowing = BorrowRecord(
        user_id=reader.id,
        book_id=book.id,
        borrow_date=datetime(2026, 6, 20),
        due_date=datetime(2026, 7, 20),
        status="borrowing",
    )
    returned = BorrowRecord(
        user_id=reader.id,
        book_id=book.id,
        borrow_date=datetime(2026, 5, 1),
        due_date=datetime(2026, 6, 1),
        return_date=datetime(2026, 5, 20),
        status="returned",
    )
    db.add_all([borrowing, returned])
    db.commit()

    data = {
        "user_id": reader.id,
        "other_user_id": other.id,
        "book_id": book.id,
        "borrowing_record_id": borrowing.id,
        "returned_record_id": returned.id,
    }
    db.close()
    return data
