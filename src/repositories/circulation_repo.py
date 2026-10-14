"""LoanRepository：借阅记录持久化。"""
from datetime import datetime

from ..domain.enums import LoanStatus
from ..domain.models import Loan


class LoanRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, loan_id: int):
        return self.session.get(Loan, loan_id)

    def get_active_by_item(self, item_id: int):
        return (
            self.session.query(Loan)
            .filter(Loan.item_id == item_id, Loan.status != LoanStatus.RETURNED.value)
            .first()
        )

    def list_by_reader(self, reader_id: int):
        return (
            self.session.query(Loan)
            .filter_by(reader_id=reader_id)
            .order_by(Loan.borrow_date.desc())
            .all()
        )

    def has_overdue(self, reader_id: int) -> bool:
        now = datetime.now()
        count = (
            self.session.query(Loan)
            .filter(
                Loan.reader_id == reader_id,
                Loan.status != LoanStatus.RETURNED.value,
                Loan.due_date < now,
            )
            .count()
        )
        return count > 0

    def save(self, loan: Loan) -> Loan:
        self.session.add(loan)
        self.session.flush()
        return loan
