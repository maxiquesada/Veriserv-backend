from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import cloudinary, cloudinary.uploader
from app.db.database import get_db
from app.models.base import Job, JobImage, Contractor
from app.schemas.schemas import JobOut
from app.core.security import get_current_user

router = APIRouter()

@router.get("/contractor/{contractor_id}", response_model=List[JobOut])
def get_contractor_jobs(contractor_id: str, db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.contratista_id == contractor_id).order_by(Job.fecha.desc()).all()

@router.post("/", response_model=JobOut, status_code=201)
async def create_job(
    descripcion: str = Form(...), fecha: date = Form(...),
    cliente_id: Optional[str] = Form(None), imagenes: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user), db: Session = Depends(get_db),
):
    contractor = db.query(Contractor).filter(Contractor.usuario_id == current_user.id).first()
    if not contractor and current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Solo contratistas pueden publicar trabajos")
    job = Job(contratista_id=contractor.id, descripcion=descripcion, fecha=fecha, cliente_id=cliente_id)
    db.add(job); db.flush()
    for i, img in enumerate(imagenes[:5]):
        if img.content_type not in ("image/jpeg", "image/png", "image/webp"): continue
        content = await img.read()
        result = cloudinary.uploader.upload(content, folder=f"veriserv/jobs/{job.id}",
            transformation=[{"width": 1200, "height": 900, "crop": "limit", "quality": "auto"}])
        db.add(JobImage(trabajo_id=job.id, url_cloudinary=result["secure_url"], public_id=result["public_id"], orden=i))
    db.commit(); db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    contractor = db.query(Contractor).filter(Contractor.usuario_id == current_user.id).first()
    if not contractor or str(job.contratista_id) != str(contractor.id):
        if current_user.tipo != "admin": raise HTTPException(status_code=403, detail="No autorizado")
    for img in job.images: cloudinary.uploader.destroy(img.public_id)
    db.delete(job); db.commit()
