"""ReaderService：读者注册。"""
from ..domain.enums import ReaderType
from ..domain.models import Reader
from ..exceptions import DuplicateError, ValidationParamError
from ..repositories import ReaderRepository


class ReaderService:
    def __init__(self, session):
        self.session = session
        self.repo = ReaderRepository(session)

    def register(self, req) -> dict:
        try:
            reader_type = ReaderType(req.reader_type).value
        except ValueError:
            raise ValidationParamError("读者类型非法")
        if self.repo.get_by_account(req.account) is not None:
            raise DuplicateError("账号已存在")

        reader = Reader(
            name=req.name,
            department=req.department,
            reader_type=reader_type,
            account=req.account,
            password=req.password,
        )
        self.repo.save(reader)
        data = {
            "reader_id": reader.reader_id,
            "name": reader.name,
            "department": reader.department,
            "reader_type": reader.reader_type,
            "account": reader.account,
        }
        self.session.commit()
        return data
