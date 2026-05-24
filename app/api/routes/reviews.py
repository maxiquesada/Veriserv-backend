from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.database import get_db
from app.models.base import Review, Job, Contractor
from app.schemas.schemas import ReviewCreate, ReviewOut
from app.core.security import get_current_user

router = APIRouter()

def recalculate_rating(contractor_id: str, db: Session):
    avg, total = db.query(func.avg(Review.estrellas), func.count(Review.id)).filter(
        Review.contratista_id == contractor_id, Review.aprobada == True).first()
    c = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if c:
        c.rating_promedio = round(float(avg or 0), 2)
        c.total_reviews = total or 0
        db.commit()

@router.get("/contractor/{contractor_id}", response_model=List[ReviewOut])
def get_contractor_reviews(contractor_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.contratista_id == contractor_id, Review.aprobada == True)\
        .order_by(Review.created_at.desc()).limit(50).all()

@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(data: ReviewCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.tipo not in ("cliente", "admin"):
        raise HTTPException(status_code=403, detail="Solo clientes pueden dejar reviews")
    job = db.query(Job).filter(Job.id == data.trabajo_id).first()
    if not job: raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    if db.query(Review).filter(Review.trabajo_id == data.trabajo_id).first():
        raise HTTPException(status_code=400, detail="Ya existe una review para este trabajo")
    review = Review(cliente_id=current_user.id, contratista_id=job.contratista_id,
        trabajo_id=data.trabajo_id, estrellas=data.estrellas, comentario=data.comentario, aprobada=False)
    db.add(review); db.commit(); db.refresh(review)
    return review
