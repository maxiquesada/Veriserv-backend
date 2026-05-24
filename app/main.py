from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, contractors, jobs, reviews, admin
from app.db.database import engine
from app.models import base as models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VeriServ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/api/auth",       tags=["Auth"])
app.include_router(users.router,       prefix="/api/users",      tags=["Users"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["Contractors"])
app.include_router(jobs.router,        prefix="/api/jobs",        tags=["Jobs"])
app.include_router(reviews.router,     prefix="/api/reviews",     tags=["Reviews"])
app.include_router(admin.router,       prefix="/api/admin",       tags=["Admin"])

@app.get("/")
def root(): return {"message": "VeriServ API v1.0", "status": "ok"}

@app.get("/health")
def health(): return {"status": "healthy"}