"""PolicyService：维护借阅规则与罚款规则。"""
from ..domain.enums import ItemType, ReaderType
from ..domain.models import BorrowPolicy, FineRule
from ..exceptions import ValidationParamError
from ..repositories import BorrowPolicyRepository, FineRuleRepository
from ..security import require_admin


class PolicyService:
    def __init__(self, session):
        self.session = session
        self.policy_repo = BorrowPolicyRepository(session)
        self.rule_repo = FineRuleRepository(session)

    def upsert_borrow_policy(self, req) -> dict:
        require_admin(self.session, req.admin_id)
        try:
            reader_type = ReaderType(req.reader_type).value
        except ValueError:
            raise ValidationParamError("读者类型非法")

        policy = self.policy_repo.get_by_reader_type(reader_type)
        if policy is None:
            policy = BorrowPolicy(
                reader_type=reader_type,
                max_borrow_count=req.max_borrow_count,
                borrow_days=req.borrow_days,
            )
        else:
            policy.max_borrow_count = req.max_borrow_count
            policy.borrow_days = req.borrow_days
        self.policy_repo.save(policy)

        data = {
            "reader_type": policy.reader_type,
            "max_borrow_count": policy.max_borrow_count,
            "borrow_days": policy.borrow_days,
        }
        self.session.commit()
        return data

    def upsert_fine_rule(self, req) -> dict:
        require_admin(self.session, req.admin_id)
        try:
            item_type = ItemType(req.item_type).value
        except ValueError:
            raise ValidationParamError("借出物类型非法")

        rule = self.rule_repo.get_by_item_type(item_type)
        if rule is None:
            rule = FineRule(item_type=item_type, rate_per_day=req.rate_per_day)
        else:
            rule.rate_per_day = req.rate_per_day
        self.rule_repo.save(rule)

        data = {"item_type": rule.item_type, "rate_per_day": float(rule.rate_per_day)}
        self.session.commit()
        return data
