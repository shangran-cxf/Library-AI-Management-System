"""ReaderRepository：读者持久化。"""
from ..domain.enums import LoanStatus
from ..domain.models import Loan, Reader


class ReaderRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, reader_id: int):
        return self.session.get(Reader, reader_id)

    def get_by_account(self, account: str):
        return self.session.query(Reader).filter_by(account=account).first()

    def save(self, reader: Reader) -> Reader:
        self.session.add(reader)
        self.session.flush()
        return reader

    def count_borrowing(self, reader_id: int) -> int:
        return (
            self.session.query(Loan)
            .filter(Loan.reader_id == reader_id, Loan.status == LoanStatus.BORROWING.value)
            .count()
        )
