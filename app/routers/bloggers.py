from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/bloggers", tags=["bloggers"])

@router.get("/", response_model=List[schemas.BloggerOut])
def list_bloggers(db: Session = Depends(get_db)):
    return db.query(models.Blogger).all()

@router.post("/", response_model=schemas.BloggerOut)
def create_blogger(payload: schemas.BloggerCreate, db: Session = Depends(get_db)):
    blogger = models.Blogger(
        platform=payload.platform,
        external_id=payload.external_id,
        handle=payload.handle,
        name=payload.name,
    )
    db.add(blogger)
    db.commit()
    db.refresh(blogger)
    return blogger
