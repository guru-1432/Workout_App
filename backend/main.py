from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
import models, schemas, crud
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic_settings import BaseSettings
from typing import Optional
import os
import secrets


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
class Settings(BaseSettings):
    authjwt_secret_key: str = "secret"
    mail_username: str = "your_email@gmail.com"
    mail_password: str = "your_password"
    mail_from: str = "your_email@gmail.com"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# --- Authentication Configuration ---
SECRET_KEY = "b5fdb6bc47e54c3139ffc538f5ed439d894385cd22c65e48d8177c27b1f45917" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    crud.create_user(db=db, user=user)
    
    # Auto-login
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/forgot-password")
async def forgot_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        # Don't reveal that the user doesn't exist
        return {"msg": "If this email is registered, you will receive a reset link."}
    
    token = secrets.token_urlsafe(32)
    crud.set_reset_token(db, user, token)
    
    reset_link = f"{settings.base_url}/reset-password.html?token={token}"
    
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user.email],
        body=f"Click the following link to reset your password: {reset_link}",
        subtype=MessageType.plain
    )
    
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Error sending email")
        
    return {"msg": "Password reset email sent"}

@app.post("/reset-password")
def reset_password(request: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    user = crud.get_user_by_reset_token(db, request.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    crud.update_user_password(db, user, request.new_password)
    return {"msg": "Password updated successfully"}

# --- Routes (Protected) ---

@app.get("/api/muscles", response_model=List[schemas.Muscle])
def read_muscles(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_muscles(db)

@app.post("/api/muscles", response_model=schemas.Muscle)
def create_muscle(muscle: schemas.MuscleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_muscle(db, muscle)

@app.delete("/api/muscles/{muscle_id}")
def delete_muscle(muscle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    crud.delete_muscle(db, muscle_id)
    return {"ok": True}

@app.get("/api/exercises", response_model=List[schemas.Exercise])
def read_all_exercises(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_all_exercises(db)

@app.post("/api/exercises", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_exercise(db, exercise)

@app.delete("/api/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    crud.delete_exercise(db, exercise_id)
    return {"ok": True}

@app.get("/api/exercises/{muscle_id}", response_model=List[schemas.Exercise])
def read_exercises_by_muscle(muscle_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_exercises_by_muscle(db, muscle_id)

@app.post("/api/log", response_model=schemas.WorkoutSession)
def log_workout(session: schemas.WorkoutSessionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_workout_session(db, session, current_user.id)

@app.get("/api/history", response_model=List[schemas.WorkoutSession])
def read_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_workout_history(db, current_user.id)

@app.get("/api/last-log/{exercise_id}", response_model=schemas.WorkoutSet)
def read_last_log(exercise_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    last_val = crud.get_last_workout_for_exercise(db, exercise_id, current_user.id)
    if not last_val:
        raise HTTPException(status_code=404, detail="No history found")
    return last_val

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_static")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
