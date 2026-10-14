"""单元测试：借阅规则策略与罚款规则策略（TC-027、TC-028）。"""
from decimal import Decimal

from src.domain.enums import ItemType, ReaderType
from src.domain.services import BorrowPolicyService, FineRuleService
from src.repositories import BorrowPolicyRepository, FineRuleRepository


def test_borrow_policy_counts_and_days(db):
    service = BorrowPolicyService(BorrowPolicyRepository(db))
    assert service.get_max_borrow_count(ReaderType.JUNIOR.value) == 3
    assert service.get_max_borrow_count(ReaderType.UNDERGRADUATE.value) == 5
    assert service.get_max_borrow_count(ReaderType.GRADUATE.value) == 10
    assert service.get_max_borrow_count(ReaderType.DOCTOR.value) == 15
    assert service.get_max_borrow_count(ReaderType.TEACHER.value) == 20

    assert service.get_borrow_days(ReaderType.JUNIOR.value) == 30
    assert service.get_borrow_days(ReaderType.UNDERGRADUATE.value) == 30
    assert service.get_borrow_days(ReaderType.GRADUATE.value) == 60
    assert service.get_borrow_days(ReaderType.DOCTOR.value) == 90
    assert service.get_borrow_days(ReaderType.TEACHER.value) == 90


def test_fine_rule_rates(db):
    service = FineRuleService(FineRuleRepository(db))
    assert service.calculate(ItemType.CHINESE_BOOK.value, 3) == Decimal("0.30")
    assert service.calculate(ItemType.FOREIGN_BOOK.value, 3) == Decimal("0.60")
    assert service.calculate(ItemType.CHINESE_MAGAZINE.value, 3) == Decimal("0.30")
    assert service.calculate(ItemType.FOREIGN_MAGAZINE.value, 3) == Decimal("0.60")
    assert service.calculate(ItemType.THESIS.value, 3) == Decimal("1.50")


def test_fine_rule_zero_when_not_overdue(db):
    service = FineRuleService(FineRuleRepository(db))
    assert service.calculate(ItemType.CHINESE_BOOK.value, 0) == Decimal("0.00")
    assert service.calculate(ItemType.CHINESE_BOOK.value, -5) == Decimal("0.00")
