"""AdminController：图书管理员维护、借阅规则与罚款规则维护。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import BorrowPolicyRequest, FineRuleRequest, LibrarianCreateRequest
from ..services.admin_service import AdminService
from ..services.policy_service import PolicyService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/librarians")
def add_librarian(req: LibrarianCreateRequest, db: Session = Depends(get_db)):
    return ok(AdminService(db).add_librarian(req))


@router.delete("/librarians/{librarian_id}")
def delete_librarian(
    librarian_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)
):
    return ok(AdminService(db).delete_librarian(librarian_id, admin_id))


@router.put("/borrow-policies")
def upsert_borrow_policy(req: BorrowPolicyRequest, db: Session = Depends(get_db)):
    return ok(PolicyService(db).upsert_borrow_policy(req))


@router.put("/fine-rules")
def upsert_fine_rule(req: FineRuleRequest, db: Session = Depends(get_db)):
    return ok(PolicyService(db).upsert_fine_rule(req))
