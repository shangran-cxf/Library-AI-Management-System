"""数据库引擎、会话与初始化（SQLite + SQLAlchemy）。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """FastAPI 依赖：提供请求级数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 默认规则（constitution / 02-requirements BR-003、BR-004、BR-007）
DEFAULT_BORROW_POLICIES = {
    "JUNIOR": (3, 30),
    "UNDERGRADUATE": (5, 30),
    "GRADUATE": (10, 60),
    "DOCTOR": (15, 90),
    "TEACHER": (20, 90),
}

DEFAULT_FINE_RULES = {
    "CHINESE_BOOK": 0.1,
    "FOREIGN_BOOK": 0.2,
    "CHINESE_MAGAZINE": 0.1,
    "FOREIGN_MAGAZINE": 0.2,
    "THESIS": 0.5,
}


def init_db(bind=None):
    """建表并写入默认借阅规则与罚款规则（幂等）。"""
    from .domain import models  # noqa: F401  确保模型已注册到 Base.metadata

    bind = bind or engine
    Base.metadata.create_all(bind=bind)
    _seed_defaults(bind)


def _seed_defaults(bind):
    from .domain.models import BorrowPolicy, FineRule

    Session = sessionmaker(bind=bind, future=True)
    with Session() as session:
        for reader_type, (max_count, days) in DEFAULT_BORROW_POLICIES.items():
            if session.query(BorrowPolicy).filter_by(reader_type=reader_type).first() is None:
                session.add(
                    BorrowPolicy(
                        reader_type=reader_type,
                        max_borrow_count=max_count,
                        borrow_days=days,
                    )
                )
        for item_type, rate in DEFAULT_FINE_RULES.items():
            if session.query(FineRule).filter_by(item_type=item_type).first() is None:
                session.add(FineRule(item_type=item_type, rate_per_day=rate))
        session.commit()
