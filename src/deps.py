"""依赖注入：提供请求级数据库会话。"""
from .database import get_db

__all__ = ["get_db"]
