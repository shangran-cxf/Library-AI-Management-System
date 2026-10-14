"""请求 DTO（Pydantic，字段 snake_case）。"""
from datetime import date

from pydantic import BaseModel


class ReaderRegisterRequest(BaseModel):
    name: str
    department: str | None = None
    reader_type: str
    account: str
    password: str | None = None


class IssueCardRequest(BaseModel):
    reader_id: int
    expire_date: date | None = None
    admin_id: int


class BorrowRequest(BaseModel):
    card_no: str
    barcode: str
    librarian_id: int


class ReturnRequest(BaseModel):
    barcode: str
    librarian_id: int


class ReservationRequest(BaseModel):
    reader_id: int
    title_id: int


class BookTitleRequest(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str | None = None
    category: str | None = None
    item_type: str
    admin_id: int


class LibraryItemRequest(BaseModel):
    title_id: int
    barcode: str
    location: str | None = None
    admin_id: int


class LibrarianCreateRequest(BaseModel):
    name: str
    account: str
    password: str | None = None
    admin_id: int


class BorrowPolicyRequest(BaseModel):
    reader_type: str
    max_borrow_count: int
    borrow_days: int
    admin_id: int


class FineRuleRequest(BaseModel):
    item_type: str
    rate_per_day: float
    admin_id: int
