import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    tipo = Column(Enum("cliente", "contratista", "admin", name="tipo_usuario"), nullable=False, default="cliente")
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    contractor = relationship("Contractor", back_populates="user", uselist=False)
    jobs_as_client = relationship("Job", back_populates="client", foreign_keys="Job.cliente_id")
    reviews_written = relationship("Review", back_populates="client", foreign_keys="Review.cliente_id")

class Contractor(Base):
    __tablename__ = "contratistas"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    rubro = Column(String(100), nullable=False, index=True)
    ubicacion = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text)
    whatsapp = Column(String(20))
    rating_promedio = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="contractor")
    jobs = relationship("Job", back_populates="contractor")
    reviews = relationship("Review", back_populates="contractor", foreign_keys="Review.contratista_id")

class Job(Base):
    __tablename__ = "trabajos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contratista_id = Column(UUID(as_uuid=True), ForeignKey("contratistas.id"), nullable=False)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    descripcion = Column(Text, nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(Enum("pendiente", "completado", "cancelado", name="estado_trabajo"), default="completado")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    contractor = relationship("Contractor", back_populates="jobs")
    client = relationship("User", back_populates="jobs_as_client", foreign_keys=[cliente_id])
    images = relationship("JobImage", back_populates="job", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="job", uselist=False)

class JobImage(Base):
    __tablename__ = "imagenes_trabajo"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trabajo_id = Column(UUID(as_uuid=True), ForeignKey("trabajos.id"), nullable=False)
    url_cloudinary = Column(String(500), nullable=False)
    public_id = Column(String(255), nullable=False)
    orden = Column(Integer, default=0)
    job = relationship("Job", back_populates="images")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    contratista_id = Column(UUID(as_uuid=True), ForeignKey("contratistas.id"), nullable=False)
    trabajo_id = Column(UUID(as_uuid=True), ForeignKey("trabajos.id"), unique=True, nullable=False)
    estrellas = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=False)
    aprobada = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    client = relationship("User", back_populates="reviews_written", foreign_keys=[cliente_id])
    contractor = relationship("Contractor", back_populates="reviews", foreign_keys=[contratista_id])
    job = relationship("Job", back_populates="review")
