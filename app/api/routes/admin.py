from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.base import User, Contractor, Review, Job
from app.schemas.schemas import UserOut, ReviewOut
from app.core.security import require_admin
from app.api.routes.reviews import recalculate_rating

router = APIRouter()

@router.get("/users", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).offset(skip).limit(limit).all()

@router.put("/users/{user_id}/toggle")
def toggle_user(user_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = not user.activo; db.commit()
    return {"id": str(user.id), "activo": user.activo}

@router.get("/reviews/pending", response_model=List[ReviewOut])
def pending_reviews(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Review).filter(Review.aprobada == False).order_by(Review.created_at.desc()).all()

@router.put("/reviews/{review_id}/approve")
def approve_review(review_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review: raise HTTPException(status_code=404, detail="Review no encontrada")
    review.aprobada = True; db.commit()
    recalculate_rating(str(review.contratista_id), db)
    return {"status": "aprobada", "id": review_id}

@router.delete("/reviews/{review_id}")
def delete_review(review_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review: raise HTTPException(status_code=404, detail="Review no encontrada")
    contractor_id = str(review.contratista_id)
    db.delete(review); db.commit()
    recalculate_rating(contractor_id, db)
    return {"status": "eliminada"}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    return {
        "total_usuarios": db.query(User).count(),
        "total_contratistas": db.query(Contractor).count(),
        "total_trabajos": db.query(Job).count(),
        "reviews_pendientes": db.query(Review).filter(Review.aprobada == False).count(),
        "reviews_aprobadas": db.query(Review).filter(Review.aprobada == True).count(),
    }
