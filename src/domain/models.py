"""领域实体（SQLAlchemy 模型）。单表继承 + 判别字段（reader_type / item_type）。"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from ..database import Base
from .enums import CardStatus, ItemStatus, LoanStatus, ReservationStatus


class Reader(Base):
    __tablename__ = "readers"

    reader_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    department = Column(String(100))
    reader_type = Column(String(20), nullable=False, index=True)
    account = Column(String(50), nullable=False, unique=True)
    password = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)

    card = relationship("BorrowCard", back_populates="reader", uselist=False)
    loans = relationship("Loan", back_populates="reader")
    reservations = relationship("Reservation", back_populates="reader")


class BorrowCard(Base):
    __tablename__ = "borrow_cards"

    card_id = Column(Integer, primary_key=True, autoincrement=True)
    card_no = Column(String(20), nullable=False, unique=True)
    reader_id = Column(Integer, ForeignKey("readers.reader_id"), nullable=False, unique=True)
    issue_date = Column(Date)
    expire_date = Column(Date)
    status = Column(String(10), nullable=False, default=CardStatus.ACTIVE.value)

    reader = relationship("Reader", back_populates="card")

    def isValid(self) -> bool:
        return self.status == CardStatus.ACTIVE.value


class Librarian(Base):
    __tablename__ = "librarians"

    librarian_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    account = Column(String(50), nullable=False, unique=True)
    password = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class SystemAdmin(Base):
    __tablename__ = "system_admins"

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    account = Column(String(50), nullable=False, unique=True)
    password = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class BookTitle(Base):
    __tablename__ = "book_titles"

    title_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    isbn = Column(String(20), nullable=False, unique=True)
    publisher = Column(String(100))
    category = Column(String(50))
    item_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    items = relationship("LibraryItem", back_populates="title", cascade="all, delete-orphan")
    reservations = relationship(
        "Reservation", back_populates="title", cascade="all, delete-orphan"
    )


class LibraryItem(Base):
    __tablename__ = "library_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(String(30), nullable=False, unique=True)
    title_id = Column(Integer, ForeignKey("book_titles.title_id"), nullable=False)
    item_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default=ItemStatus.AVAILABLE.value, index=True)
    location = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    title = relationship("BookTitle", back_populates="items")
    loans = relationship("Loan", back_populates="item")

    def isAvailable(self) -> bool:
        return self.status == ItemStatus.AVAILABLE.value

    def markBorrowed(self) -> None:
        self.status = ItemStatus.BORROWED.value

    def markAvailable(self) -> None:
        self.status = ItemStatus.AVAILABLE.value


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, autoincrement=True)
    reader_id = Column(Integer, ForeignKey("readers.reader_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("library_items.item_id"), nullable=False)
    borrow_date = Column(DateTime, nullable=False, default=datetime.now)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime)
    status = Column(String(20), nullable=False, default=LoanStatus.BORROWING.value, index=True)
    is_overdue = Column(Boolean, nullable=False, default=False)

    reader = relationship("Reader", back_populates="loans")
    item = relationship("LibraryItem", back_populates="loans")
    fines = relationship("FineRecord", back_populates="loan")

    def isReturned(self) -> bool:
        return self.status == LoanStatus.RETURNED.value

    def overdueDays(self, at: datetime | None = None) -> int:
        at = at or datetime.now()
        if self.due_date is None:
            return 0
        delta = (at.date() - self.due_date.date()).days
        return delta if delta > 0 else 0


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, autoincrement=True)
    reader_id = Column(Integer, ForeignKey("readers.reader_id"), nullable=False)
    title_id = Column(Integer, ForeignKey("book_titles.title_id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
    status = Column(String(20), nullable=False, default=ReservationStatus.ACTIVE.value)
    queue_position = Column(Integer)

    reader = relationship("Reader", back_populates="reservations")
    title = relationship("BookTitle", back_populates="reservations")

    def isActive(self) -> bool:
        return self.status == ReservationStatus.ACTIVE.value


class BorrowPolicy(Base):
    __tablename__ = "borrow_policies"

    policy_id = Column(Integer, primary_key=True, autoincrement=True)
    reader_type = Column(String(20), nullable=False, unique=True)
    max_borrow_count = Column(Integer, nullable=False)
    borrow_days = Column(Integer, nullable=False)


class FineRule(Base):
    __tablename__ = "fine_rules"

    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(20), nullable=False, unique=True)
    rate_per_day = Column(Numeric(6, 2), nullable=False)


class FineRecord(Base):
    __tablename__ = "fine_records"

    fine_id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("readers.reader_id"), nullable=False)
    item_type = Column(String(20), nullable=False)
    overdue_days = Column(Integer, nullable=False)
    amount = Column(Numeric(8, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), nullable=False, default="UNPAID")

    loan = relationship("Loan", back_populates="fines")
