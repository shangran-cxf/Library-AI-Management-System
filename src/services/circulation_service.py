"""CirculationService：借书、还书、查询借阅信息。"""
from datetime import datetime

from ..domain.enums import LoanStatus
from ..domain.models import Loan
from ..domain.services import BorrowPolicyService
from ..exceptions import (
    BorrowLimitExceededError,
    CardInvalidError,
    ItemNotAvailableError,
    NotFoundError,
    OverdueBooksError,
    PermissionDeniedError,
)
from ..repositories import (
    BorrowCardRepository,
    BorrowPolicyRepository,
    LibraryItemRepository,
    LoanRepository,
    ReaderRepository,
)
from ..security import require_librarian
from .fine_service import FineService


class CirculationService:
    def __init__(self, session):
        self.session = session
        self.card_repo = BorrowCardRepository(session)
        self.reader_repo = ReaderRepository(session)
        self.item_repo = LibraryItemRepository(session)
        self.loan_repo = LoanRepository(session)
        self.policy_repo = BorrowPolicyRepository(session)

    # ---- UC-101 办理借书 ----
    def borrow(self, card_no: str, barcode: str, librarian_id: int) -> dict:
        require_librarian(self.session, librarian_id)

        card = self.card_repo.get_by_card_no(card_no)
        if card is None or not card.isValid():
            raise CardInvalidError("借阅证无效")

        reader = self.reader_repo.get_by_id(card.reader_id)
        if reader is None:
            raise NotFoundError("读者不存在")

        policy = BorrowPolicyService(self.policy_repo)
        current = self.reader_repo.count_borrowing(reader.reader_id)
        if current >= policy.get_max_borrow_count(reader.reader_type):
            raise BorrowLimitExceededError("借阅已满")
        if self.loan_repo.has_overdue(reader.reader_id):
            raise OverdueBooksError("请先归还超期图书")

        item = self.item_repo.get_by_barcode(barcode)
        if item is None or not item.isAvailable():
            raise ItemNotAvailableError("图书不可借")

        borrow_date = datetime.now()
        due_date = policy.calc_due_date(reader.reader_type, borrow_date)
        loan = Loan(
            reader_id=reader.reader_id,
            item_id=item.item_id,
            borrow_date=borrow_date,
            due_date=due_date,
            status=LoanStatus.BORROWING.value,
            is_overdue=False,
        )
        self.loan_repo.save(loan)
        item.markBorrowed()
        self.item_repo.save(item)

        data = {
            "loan_id": loan.loan_id,
            "reader_id": reader.reader_id,
            "item_id": item.item_id,
            "barcode": item.barcode,
            "borrow_date": borrow_date,
            "due_date": due_date,
            "status": loan.status,
        }
        self.session.commit()
        return data

    # ---- UC-102 办理还书（含 UC-110 罚款计算） ----
    def return_book(self, barcode: str, librarian_id: int) -> dict:
        require_librarian(self.session, librarian_id)

        item = self.item_repo.get_by_barcode(barcode)
        if item is None:
            raise NotFoundError("非本馆藏书")

        loan = self.loan_repo.get_active_by_item(item.item_id)
        if loan is None:
            raise NotFoundError("未找到借阅记录")

        return_date = datetime.now()
        loan.return_date = return_date
        loan.status = LoanStatus.RETURNED.value
        item.markAvailable()
        self.item_repo.save(item)

        fine = FineService(self.session).calculate_and_record(loan, return_date)

        data = {
            "loan_id": loan.loan_id,
            "return_date": return_date,
            "overdue_days": fine.overdue_days if fine is not None else 0,
            "fine_amount": float(fine.amount) if fine is not None else 0.0,
            "fine_id": fine.fine_id if fine is not None else None,
        }
        self.session.commit()
        return data

    # ---- UC-003 / UC-103 查询借阅信息 ----
    def query_loans(self, reader_id: int, operator_type: str, operator_id) -> list:
        reader = self.reader_repo.get_by_id(reader_id)
        if reader is None:
            raise NotFoundError("读者不存在")

        if operator_type == "reader":
            if operator_id is None or int(operator_id) != int(reader_id):
                raise PermissionDeniedError("无权限查看该读者借阅信息")
        elif operator_type == "librarian":
            require_librarian(self.session, operator_id)
        else:
            raise PermissionDeniedError("无权限查看该读者借阅信息")

        result = []
        for loan in self.loan_repo.list_by_reader(reader_id):
            item = self.item_repo.get_by_id(loan.item_id)
            title = item.title.title if item is not None and item.title is not None else None
            is_overdue = bool(loan.is_overdue) or (
                not loan.isReturned() and loan.overdueDays() > 0
            )
            result.append(
                {
                    "loan_id": loan.loan_id,
                    "item_id": loan.item_id,
                    "title": title,
                    "borrow_date": loan.borrow_date,
                    "due_date": loan.due_date,
                    "return_date": loan.return_date,
                    "status": loan.status,
                    "is_overdue": is_overdue,
                }
            )
        return result
