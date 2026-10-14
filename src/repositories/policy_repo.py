"""规则与罚款持久化：借阅规则、罚款规则、罚款记录。"""
from ..domain.models import BorrowPolicy, FineRecord, FineRule


class BorrowPolicyRepository:
    def __init__(self, session):
        self.session = session

    def get_by_reader_type(self, reader_type: str):
        return self.session.query(BorrowPolicy).filter_by(reader_type=reader_type).first()

    def list_all(self):
        return self.session.query(BorrowPolicy).all()

    def save(self, policy: BorrowPolicy) -> BorrowPolicy:
        self.session.add(policy)
        self.session.flush()
        return policy


class FineRuleRepository:
    def __init__(self, session):
        self.session = session

    def get_by_item_type(self, item_type: str):
        return self.session.query(FineRule).filter_by(item_type=item_type).first()

    def list_all(self):
        return self.session.query(FineRule).all()

    def save(self, rule: FineRule) -> FineRule:
        self.session.add(rule)
        self.session.flush()
        return rule


class FineRecordRepository:
    def __init__(self, session):
        self.session = session

    def list_by_reader(self, reader_id: int):
        return self.session.query(FineRecord).filter_by(reader_id=reader_id).all()

    def save(self, fine: FineRecord) -> FineRecord:
        self.session.add(fine)
        self.session.flush()
        return fine
