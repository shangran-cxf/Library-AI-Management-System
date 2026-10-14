"""FineService：计算超期罚款并生成罚款记录（被还书用例包含）。"""
from decimal import Decimal

from ..domain.enums import FineStatus
from ..domain.models import FineRecord
from ..domain.services import FineRuleService
from ..repositories import FineRecordRepository, FineRuleRepository, LibraryItemRepository


class FineService:
    def __init__(self, session):
        self.session = session
        self.item_repo = LibraryItemRepository(session)
        self.fine_repo = FineRecordRepository(session)
        self.rule_service = FineRuleService(FineRuleRepository(session))

    def calculate_and_record(self, loan, return_date):
        """超期则生成 FineRecord 并返回；未超期返回 None。"""
        item = self.item_repo.get_by_id(loan.item_id)
        item_type = item.item_type if item is not None else None

        overdue_days = self.rule_service.overdue_days(loan.due_date, return_date)
        if overdue_days <= 0:
            loan.is_overdue = False
            return None

        amount = self.rule_service.calculate(item_type, overdue_days)
        loan.is_overdue = True

        fine = FineRecord(
            loan_id=loan.loan_id,
            reader_id=loan.reader_id,
            item_type=item_type,
            overdue_days=overdue_days,
            amount=amount,
            status=FineStatus.UNPAID.value,
        )
        self.fine_repo.save(fine)
        return fine
