from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas
import auth
from auth import get_current_user
import shutil
import os
import random
from datetime import datetime, timedelta
from resume_parser import extract_text
from matcher import compute_similarity
from email_utils import send_otp_email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploaded_resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {"message": "Resume Matcher API is running"}


@app.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = auth.hash_password(user.password)
    otp = str(random.randint(100000, 999999))

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw,
        is_verified=False,
        otp_code=otp,
        otp_expiry=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_otp_email(user.email, otp)

    return new_user


@app.post("/verify-otp")
def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}
    if user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP expired, please request a new one")

    user.is_verified = True
    user.otp_code = None
    user.otp_expiry = None
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@app.post("/resend-otp")
def resend_otp(data: schemas.ResendOTP, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email already verified"}

    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    send_otp_email(user.email, otp)
    return {"message": "A new OTP has been sent to your email"}


@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/resumes/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text(file_path)

    new_resume = models.Resume(
        user_id=current_user.id,
        filename=file.filename,
        extracted_text=extracted_text,
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "id": new_resume.id,
        "filename": new_resume.filename,
        "extracted_text_preview": extracted_text[:200],
    }


@app.get("/resumes", response_model=list[schemas.ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Resume).filter(models.Resume.user_id == current_user.id).all()


@app.post("/jobs", response_model=schemas.JobOut)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    new_job = models.Job(title=job.title, company=job.company, description=job.description)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


@app.post("/resumes/{resume_id}/match")
def match_resume_to_jobs(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jobs = db.query(models.Job).all()
    results = []

    for job in jobs:
        score = compute_similarity(resume.extracted_text, job.description)

        match = models.Match(resume_id=resume.id, job_id=job.id, score=score)
        db.add(match)

        results.append({
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "description": job.description[:220] + ("..." if len(job.description) > 220 else ""),
            "url": job.url,
            "location": job.location,
            "experience_level": job.experience_level,
            "work_type": job.work_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "score": round(score, 4)
        })

    db.commit()

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"resume_id": resume.id, "matches": results}

@app.delete("/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resume = db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete related matches first (same foreign key issue as jobs)
    db.query(models.Match).filter(models.Match.resume_id == resume_id).delete()

    # Delete the physical file too, not just the database row
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{resume.filename}")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(resume)
    db.commit()

    return {"message": "Resume deleted successfully"}