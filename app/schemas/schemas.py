from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum

class TipoUsuario(str, Enum):
    cliente = "cliente"
    contratista = "contratista"
    admin = "admin"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    tipo: TipoUsuario = TipoUsuario.cliente

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tipo: str

class UserOut(BaseModel):
    id: UUID
    email: str
    tipo: str
    activo: bool
    created_at: datetime
    class Config:
        from_attributes = True

class ContractorCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=255)
    rubro: str = Field(min_length=2, max_length=100)
    ubicacion: str = Field(min_length=2, max_length=255)
    descripcion: Optional[str] = None
    whatsapp: Optional[str] = None

class ContractorUpdate(BaseModel):
    nombre: Optional[str] = None
    rubro: Optional[str] = None
    ubicacion: Optional[str] = None
    descripcion: Optional[str] = None
    whatsapp: Optional[str] = None

class ImageOut(BaseModel):
    id: UUID
    url_cloudinary: str
    orden: int
    class Config:
        from_attributes = True

class JobOut(BaseModel):
    id: UUID
    contratista_id: UUID
    cliente_id: Optional[UUID]
    descripcion: str
    fecha: date
    estado: str
    created_at: datetime
    images: List[ImageOut] = []
    class Config:
        from_attributes = True

class ReviewOut(BaseModel):
    id: UUID
    cliente_id: UUID
    contratista_id: UUID
    trabajo_id: UUID
    estrellas: int
    comentario: str
    aprobada: bool
    created_at: datetime
    class Config:
        from_attributes = True

class ContractorOut(BaseModel):
    id: UUID
    usuario_id: UUID
    nombre: str
    rubro: str
    ubicacion: str
    descripcion: Optional[str]
    whatsapp: Optional[str]
    rating_promedio: float
    total_reviews: int
    created_at: datetime
    class Config:
        from_attributes = True

class ContractorDetail(ContractorOut):
    jobs: List[JobOut] = []
    reviews: List[ReviewOut] = []

class ReviewCreate(BaseModel):
    trabajo_id: UUID
    estrellas: int = Field(ge=1, le=5)
    comentario: str = Field(min_length=10)
