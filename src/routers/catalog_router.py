"""CatalogController：图书查询、图书标题与馆藏副本维护。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..response import ok
from ..schemas import BookTitleRequest, LibraryItemRequest
from ..services.catalog_service import CatalogService

router = APIRouter(prefix="/api", tags=["catalog"])


@router.get("/books")
def search_books(
    keyword: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    return ok(CatalogService(db).search(keyword, category))


@router.post("/admin/book-titles")
def add_book_title(req: BookTitleRequest, db: Session = Depends(get_db)):
    return ok(CatalogService(db).add_title(req, req.admin_id))


@router.delete("/admin/book-titles/{title_id}")
def delete_book_title(
    title_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)
):
    return ok(CatalogService(db).delete_title(title_id, admin_id))


@router.post("/admin/library-items")
def add_library_item(req: LibraryItemRequest, db: Session = Depends(get_db)):
    return ok(CatalogService(db).add_item(req, req.admin_id))


@router.delete("/admin/library-items/{item_id}")
def delete_library_item(
    item_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)
):
    return ok(CatalogService(db).delete_item(item_id, admin_id))
