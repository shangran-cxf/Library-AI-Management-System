"""领域服务：借阅规则策略与罚款规则策略（Strategy 的封装）。"""
from datetime import datetime, timedelta
from decimal import Decimal

from ..exceptions import BusinessRuleError
from ..repositories import BorrowPolicyRepository, FineRuleRepository


class BorrowPolicyService:
    """按读者类型给出借阅数量与期限。"""

    def __init__(self, policy_repo: BorrowPolicyRepository):
        self.policy_repo = policy_repo

    def _policy(self, reader_type):
        policy = self.policy_repo.get_by_reader_type(reader_type)
        if policy is None:
            raise BusinessRuleError(f"未配置读者类型借阅规则：{reader_type}")
        return policy

    def get_max_borrow_count(self, reader_type) -> int:
        return self._policy(reader_type).max_borrow_count

    def get_borrow_days(self, reader_type) -> int:
        return self._policy(reader_type).borrow_days

    def calc_due_date(self, reader_type, borrow_date: datetime) -> datetime:
        return borrow_date + timedelta(days=self.get_borrow_days(reader_type))

    def can_borrow(self, reader, current_count: int) -> bool:
        return current_count < self.get_max_borrow_count(reader.reader_type)


class FineRuleService:
    """按借出物类型给出超期费率并计算罚金。"""

    def __init__(self, fine_rule_repo: FineRuleRepository):
        self.fine_rule_repo = fine_rule_repo

    def overdue_days(self, due_date, return_date: datetime) -> int:
        if due_date is None:
            return 0
        delta = (return_date.date() - due_date.date()).days
        return delta if delta > 0 else 0

    def get_rate(self, item_type) -> Decimal:
        rule = self.fine_rule_repo.get_by_item_type(item_type)
        if rule is None:
            raise BusinessRuleError(f"未配置借出物罚款规则：{item_type}")
        return Decimal(str(rule.rate_per_day))

    def calculate(self, item_type, overdue_days: int) -> Decimal:
        if overdue_days <= 0:
            return Decimal("0.00")
        return (self.get_rate(item_type) * overdue_days).quantize(Decimal("0.01"))
