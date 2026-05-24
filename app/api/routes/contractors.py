from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import cloudinary, cloudinary.uploader
from app.db.database import get_db
from app.models.base import Contractor
from app.schemas.schemas import ContractorCreate, ContractorUpdate, ContractorOut, ContractorDetail
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()
cloudinary.config(cloud_name=settings.CLOUDINARY_CLOUD_NAME, api_key=settings.CLOUDINARY_API_KEY, api_secret=settings.CLOUDINARY_API_SECRET)

@router.get("/", response_model=List[ContractorOut])
def list_contractors(
    rubro: Optional[str] = Query(None), ubicacion: Optional[str] = Query(None),
    orden: str = Query("rating"), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(Contractor)
    if rubro: q = q.filter(Contractor.rubro.ilike(f"%{rubro}%"))
    if ubicacion: q = q.filter(Contractor.ubicacion.ilike(f"%{ubicacion}%"))
    if orden == "rating": q = q.order_by(Contractor.rating_promedio.desc(), Contractor.total_reviews.desc())
    else: q = q.order_by(Contractor.created_at.desc())
    return q.offset((page - 1) * limit).limit(limit).all()

@router.get("/rubros/list")
def list_rubros(db: Session = Depends(get_db)):
    return sorted(set(r[0] for r in db.query(Contractor.rubro).distinct().all()))

@router.get("/{contractor_id}", response_model=ContractorDetail)
def get_contractor(contractor_id: str, db: Session = Depends(get_db)):
    c = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not c: raise HTTPException(status_code=404, detail="Contratista no encontrado")
    return c

@router.post("/", response_model=ContractorOut, status_code=201)
def create_contractor(data: ContractorCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.tipo not in ("contratista", "admin"):
        raise HTTPException(status_code=403, detail="Solo contratistas pueden crear perfiles")
    if current_user.contractor:
        raise HTTPException(status_code=400, detail="Ya tenés un perfil de contratista")
    contractor = Contractor(usuario_id=current_user.id, **data.model_dump())
    db.add(contractor); db.commit(); db.refresh(contractor)
    return contractor

@router.put("/{contractor_id}", response_model=ContractorOut)
def update_contractor(contractor_id: str, data: ContractorUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not c: raise HTTPException(status_code=404, detail="Contratista no encontrado")
    if str(c.usuario_id) != str(current_user.id) and current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(c, field, value)
    db.commit(); db.refresh(c)
    return c
