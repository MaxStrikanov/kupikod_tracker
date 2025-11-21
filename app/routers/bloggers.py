from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/bloggers", tags=["bloggers"])


@router.post("/", response_model=schemas.BloggerRead)
def create_blogger(
    data: schemas.BloggerCreate,
    db: Session = Depends(get_db),
):
    blogger = (
        db.query(models.Blogger)
        .filter(
            models.Blogger.platform == data.platform,
            models.Blogger.external_id == data.external_id,
        )
        .first()
    )
    if blogger:
        raise HTTPException(status_code=400, detail="Blogger already exists")

    blogger = models.Blogger(
        platform=data.platform,
        external_id=data.external_id,
        handle=data.handle,
        name=data.name,
    )
    db.add(blogger)
    db.commit()
    db.refresh(blogger)
    return blogger


@router.get("/", response_model=List[schemas.BloggerRead])
def list_bloggers(db: Session = Depends(get_db)):
    bloggers = db.query(models.Blogger).all()
    return bloggers
