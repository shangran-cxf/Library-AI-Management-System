"""
原子能力API路由
每个端点代表一个原子操作，供Agent调用
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import json
import sys

# Windows 控制台默认 GBK，重设为 UTF-8 避免中文/emoji 打印崩溃
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from .models import (
    SessionLocal, User, Book, BorrowRecord, Review,
    init_database, engine, Base
)

# 创建FastAPI应用
app = FastAPI(title="图书管理系统 - 原子能力API", version="1.0.0")

# ========== DTO（数据传输对象）定义 ==========

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class BookSearchParam(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    location: Optional[str] = None

class BorrowRequest(BaseModel):
    user_id: int
    book_id: int

class ReturnRequest(BaseModel):
    record_id: int

class RenewRequest(BaseModel):
    """续借请求（任务一）"""
    record_id: int
    extend_days: Optional[int] = 30  # 延长天数，默认 30 天

class ReviewRequest(BaseModel):
    """发表评论请求（任务二）"""
    user_id: int
    rating: int                      # 评分 1-5
    comment: Optional[str] = None    # 评论内容

class APIResponse(BaseModel):
    code: int  # 200成功，400业务错误，500系统错误
    message: str
    data: Optional[dict] = None

# ========== 依赖注入 ==========

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== 原子能力接口 ==========

@app.post("/api/login", response_model=LoginResponse, tags=["用户管理"])
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录认证
    """
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        return LoginResponse(success=False, message="用户不存在")
    if user.password != req.password:
        return LoginResponse(success=False, message="密码错误")
    
    return LoginResponse(
        success=True,
        message="登录成功",
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "max_borrow": user.max_borrow
        }
    )

@app.get("/api/users/{user_id}", response_model=APIResponse, tags=["用户管理"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    查询用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "max_borrow": user.max_borrow,
            "email": user.email
        }
    )

@app.get("/api/books/search", response_model=APIResponse, tags=["图书检索"])
def search_books(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="图书分类"),
    author: Optional[str] = Query(None, description="作者"),
    location: Optional[str] = Query(None, description="馆藏位置"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    图书检索（支持多条件组合查询）
    """
    query = db.query(Book).filter(Book.is_active == True)
    
    # 关键词搜索（书名或ISBN）
    if keyword:
        query = query.filter(
            or_(
                Book.title.contains(keyword),
                Book.isbn.contains(keyword)
            )
        )
    
    # 分类过滤
    if category:
        query = query.filter(Book.category == category)
    
    # 作者过滤
    if author:
        query = query.filter(Book.author.contains(author))
    
    # 馆藏位置过滤
    if location:
        query = query.filter(Book.location.contains(location))
    
    # 计算总数
    total = query.count()
    
    # 分页
    books = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 序列化结果
    book_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publisher": book.publisher,
            "category": book.category,
            "location": book.location,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "status": "在馆" if book.available_copies > 0 else "已借出",
            "description": book.description
        }
        for book in books
    ]
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "books": book_list
        }
    )

@app.get("/api/books/{book_id}", response_model=APIResponse, tags=["图书检索"])
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    """
    获取图书详情
    """
    book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not book:
        return APIResponse(code=404, message="图书不存在")
    
    # 查询当前借阅记录
    current_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.status == "borrowing"
    ).count()
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publisher": book.publisher,
            "published_year": book.published_year,
            "category": book.category,
            "location": book.location,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "current_borrowed": current_borrow,
            "status": "在馆" if book.available_copies > 0 else "已借出",
            "description": book.description
        }
    )

@app.get("/api/books", response_model=APIResponse, tags=["图书检索"])
def list_all_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    列出所有图书（分页）
    """
    total = db.query(Book).filter(Book.is_active == True).count()
    books = db.query(Book).filter(Book.is_active == True)\
        .offset((page - 1) * page_size).limit(page_size).all()
    
    book_list = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "category": book.category,
            "location": book.location,
            "available_copies": book.available_copies,
            "status": "在馆" if book.available_copies > 0 else "已借出"
        }
        for book in books
    ]
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={"total": total, "books": book_list}
    )

@app.get("/api/borrow/check-quota/{user_id}", response_model=APIResponse, tags=["借阅管理"])
def check_borrow_quota(user_id: int, db: Session = Depends(get_db)):
    """
    检查用户借阅配额
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return APIResponse(code=404, message="用户不存在")
    
    # 查询当前借阅数量
    current_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == user_id,
        BorrowRecord.status == "borrowing"
    ).count()
    
    # 检查是否有超期未还记录
    overdue_records = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == user_id,
        BorrowRecord.status == "borrowing",
        BorrowRecord.due_date < datetime.now()
    ).count()
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={
            "user_id": user.id,
            "username": user.username,
            "current_borrowed": current_borrow,
            "max_borrow": user.max_borrow,
            "remaining": user.max_borrow - current_borrow,
            "has_overdue": overdue_records > 0,
            "overdue_count": overdue_records
        }
    )

@app.post("/api/borrow", response_model=APIResponse, tags=["借阅管理"])
def borrow_book(req: BorrowRequest, db: Session = Depends(get_db)):
    """
    借阅图书
    完整流程：验证用户 → 检查配额 → 检查图书 → 更新库存 → 创建记录
    """
    # 第1步：验证用户
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        return APIResponse(code=400, message="用户不存在")
    if user.role == "admin":
        return APIResponse(code=400, message="管理员不能借书")
    
    # 第2步：检查借阅配额
    current_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == req.user_id,
        BorrowRecord.status == "borrowing"
    ).count()
    if current_borrow >= user.max_borrow:
        return APIResponse(code=400, message=f"借阅已满（{current_borrow}/{user.max_borrow}），请先归还图书")
    
    # 第3步：检查超期记录
    overdue = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == req.user_id,
        BorrowRecord.status == "borrowing",
        BorrowRecord.due_date < datetime.now()
    ).count()
    if overdue > 0:
        return APIResponse(code=400, message=f"有{overdue}本图书超期未还，请先归还")
    
    # 第4步：检查图书状态
    book = db.query(Book).filter(Book.id == req.book_id, Book.is_active == True).first()
    if not book:
        return APIResponse(code=400, message="图书不存在")
    if book.available_copies <= 0:
        return APIResponse(code=400, message="图书已全部借出")
    
    # 第5步：执行借阅操作（事务）
    try:
        # 减少可借复本
        book.available_copies -= 1
        
        # 创建借阅记录
        due_date = datetime.now() + timedelta(days=30)
        record = BorrowRecord(
            user_id=req.user_id,
            book_id=req.book_id,
            borrow_date=datetime.now(),
            due_date=due_date,
            status="borrowing"
        )
        db.add(record)
        db.commit()
        
        return APIResponse(
            code=200,
            message="借阅成功",
            data={
                "record_id": record.id,
                "book_title": book.title,
                "user_name": user.username,
                "borrow_date": record.borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "remaining_quota": user.max_borrow - current_borrow - 1
            }
        )
    except Exception as e:
        db.rollback()
        return APIResponse(code=500, message=f"借阅失败：{str(e)}")

@app.post("/api/return", response_model=APIResponse, tags=["借阅管理"])
def return_book(req: ReturnRequest, db: Session = Depends(get_db)):
    """
    归还图书
    """
    record = db.query(BorrowRecord).filter(
        BorrowRecord.id == req.record_id,
        BorrowRecord.status == "borrowing"
    ).first()
    
    if not record:
        return APIResponse(code=400, message="借阅记录不存在或已归还")
    
    try:
        # 更新借阅记录
        record.return_date = datetime.now()
        record.status = "returned"
        
        # 计算是否超期
        if datetime.now() > record.due_date:
            days_overdue = (datetime.now() - record.due_date).days
            record.is_overdue = True
            fine = days_overdue * 0.5  # 每天0.5元
        else:
            days_overdue = 0
            fine = 0
        
        # 增加图书可借复本
        book = db.query(Book).filter(Book.id == record.book_id).first()
        book.available_copies += 1
        
        db.commit()
        
        return APIResponse(
            code=200,
            message="归还成功",
            data={
                "book_title": book.title,
                "borrow_date": record.borrow_date.strftime("%Y-%m-%d"),
                "return_date": record.return_date.strftime("%Y-%m-%d"),
                "days_overdue": days_overdue,
                "fine": fine
            }
        )
    except Exception as e:
        db.rollback()
        return APIResponse(code=500, message=f"归还失败：{str(e)}")

@app.get("/api/borrow/records/{user_id}", response_model=APIResponse, tags=["借阅管理"])
def get_borrow_records(user_id: int, status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    查询用户的借阅记录
    """
    query = db.query(BorrowRecord).filter(BorrowRecord.user_id == user_id)
    
    if status:
        query = query.filter(BorrowRecord.status == status)
    
    records = query.order_by(BorrowRecord.borrow_date.desc()).all()
    
    record_list = [
        {
            "record_id": r.id,
            "book_title": r.book.title,
            "book_author": r.book.author,
            "borrow_date": r.borrow_date.strftime("%Y-%m-%d"),
            "due_date": r.due_date.strftime("%Y-%m-%d"),
            "return_date": r.return_date.strftime("%Y-%m-%d") if r.return_date else None,
            "status": r.status,
            "is_overdue": r.is_overdue
        }
        for r in records
    ]
    
    return APIResponse(
        code=200,
        message="查询成功",
        data={"records": record_list, "total": len(record_list)}
    )

@app.post("/api/renew", response_model=APIResponse, tags=["借阅管理"])
def renew_book(req: RenewRequest, db: Session = Depends(get_db)):
    """
    续借图书（任务一）
    仅状态为 borrowing（在借）的记录可续借；已归还的记录返回业务错误。
    将应还日期在原基础上延长 extend_days 天，返回新的应还日期 new_due_date。
    """
    # 第1步：定位借阅记录，仅在借状态可续借
    record = db.query(BorrowRecord).filter(BorrowRecord.id == req.record_id).first()
    if not record:
        return APIResponse(code=400, message="借阅记录不存在")
    if record.status != "borrowing":
        return APIResponse(code=400, message="该记录已归还，无法续借")

    # 第2步：校验延长天数
    if req.extend_days is None or req.extend_days <= 0:
        return APIResponse(code=400, message="延长天数必须为正整数")

    # 第3步：延长应还日期
    try:
        old_due_date = record.due_date
        new_due_date = old_due_date + timedelta(days=req.extend_days)
        record.due_date = new_due_date
        db.commit()

        book = db.query(Book).filter(Book.id == record.book_id).first()
        return APIResponse(
            code=200,
            message=f"续借成功！新的应还日期为 {new_due_date.strftime('%Y-%m-%d')}。",
            data={
                "record_id": record.id,
                "book_title": book.title if book else None,
                "old_due_date": old_due_date.strftime("%Y-%m-%d"),
                "new_due_date": new_due_date.strftime("%Y-%m-%d"),
                "extend_days": req.extend_days
            }
        )
    except Exception as e:
        db.rollback()
        return APIResponse(code=500, message=f"续借失败：{str(e)}")

@app.post("/api/books/reserve", response_model=APIResponse, tags=["预约管理"])
def reserve_book(req: BorrowRequest, db: Session = Depends(get_db)):
    """
    预约图书（当图书已借出时）
    """
    book = db.query(Book).filter(Book.id == req.book_id, Book.is_active == True).first()
    if not book:
        return APIResponse(code=400, message="图书不存在")
    
    if book.available_copies > 0:
        return APIResponse(code=400, message="图书在馆，请直接借阅")
    
    # 检查是否已经预约过
    existing = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == req.user_id,
        BorrowRecord.book_id == req.book_id,
        BorrowRecord.status == "reserved"
    ).first()
    
    if existing:
        return APIResponse(code=400, message="您已经预约过这本书了")
    
    try:
        record = BorrowRecord(
            user_id=req.user_id,
            book_id=req.book_id,
            borrow_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=7),
            status="reserved"
        )
        db.add(record)
        db.commit()
        
        return APIResponse(
            code=200,
            message="预约成功，图书到馆后将通知您",
            data={"record_id": record.id, "book_title": book.title}
        )
    except Exception as e:
        db.rollback()
        return APIResponse(code=500, message=f"预约失败：{str(e)}")

@app.post("/api/books/{book_id}/reviews", response_model=APIResponse, tags=["评论管理"])
def add_review(book_id: int, req: ReviewRequest, db: Session = Depends(get_db)):
    """
    发表图书评论与评分（任务二）
    校验图书存在、用户存在、评分在 1-5 范围；超出范围返回业务错误。
    """
    # 第1步：校验图书
    book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not book:
        return APIResponse(code=400, message="图书不存在")

    # 第2步：校验用户
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        return APIResponse(code=400, message="用户不存在")

    # 第3步：校验评分范围 1-5
    if req.rating is None or req.rating < 1 or req.rating > 5:
        return APIResponse(code=400, message="评分必须在 1-5 之间")

    # 第4步：保存评论
    try:
        review = Review(
            book_id=book_id,
            user_id=req.user_id,
            rating=req.rating,
            comment=req.comment
        )
        db.add(review)
        db.commit()

        return APIResponse(
            code=200,
            message="评论发表成功",
            data={
                "review_id": review.id,
                "book_id": book.id,
                "book_title": book.title,
                "user_id": user.id,
                "username": user.username,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        )
    except Exception as e:
        db.rollback()
        return APIResponse(code=500, message=f"评论失败：{str(e)}")

@app.get("/api/books/{book_id}/reviews", response_model=APIResponse, tags=["评论管理"])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    """
    查看某本图书的全部评论与平均评分（任务二）
    平均评分由后端计算，保留 1 位小数；无评论时为 0。
    """
    book = db.query(Book).filter(Book.id == book_id, Book.is_active == True).first()
    if not book:
        return APIResponse(code=404, message="图书不存在")

    reviews = db.query(Review).filter(Review.book_id == book_id)\
        .order_by(Review.created_at.desc()).all()

    total = len(reviews)
    average_rating = round(sum(r.rating for r in reviews) / total, 1) if total > 0 else 0

    review_list = [
        {
            "review_id": r.id,
            "user_id": r.user_id,
            "username": r.user.username if r.user else None,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in reviews
    ]

    return APIResponse(
        code=200,
        message="查询成功",
        data={
            "book_id": book.id,
            "book_title": book.title,
            "average_rating": average_rating,
            "total": total,
            "reviews": review_list
        }
    )

@app.get("/api/health", tags=["系统管理"])
def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ========== 启动服务 ==========

def start_server(port: int = 8001):
    """启动FastAPI服务"""
    import uvicorn
    print("正在启动图书管理系统API服务...")
    print(f"API文档地址：http://localhost:{port}/docs")
    print("原子能力接口已就绪，等待Agent调用")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # 初始化数据库
    init_database()
    # 启动服务
    start_server()
