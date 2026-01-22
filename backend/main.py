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
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Configuration ---
SECRET_KEY = "b5fdb6bc47e54c3139ffc538f5ed439d894385cd22c65e48d8177c27b1f45917" # Generated random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Hardcoded user credentials as requested
FAKE_USERS_DB = {
    "GPU": {
        "username": "GPU",
        "password": "Gp119", # In a real app, hash this!
    }
}

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

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = FAKE_USERS_DB.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or user['password'] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Routes (Protected) ---

@app.get("/api/muscles", response_model=List[schemas.Muscle])
def read_muscles(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_muscles(db)

@app.post("/api/muscles", response_model=schemas.Muscle)
def create_muscle(muscle: schemas.MuscleCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_muscle(db, muscle)

@app.delete("/api/muscles/{muscle_id}")
def delete_muscle(muscle_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    crud.delete_muscle(db, muscle_id)
    return {"ok": True}

@app.get("/api/exercises", response_model=List[schemas.Exercise])
def read_all_exercises(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_all_exercises(db)

@app.post("/api/exercises", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_exercise(db, exercise)

@app.delete("/api/exercises/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    crud.delete_exercise(db, exercise_id)
    return {"ok": True}

@app.get("/api/exercises/{muscle_id}", response_model=List[schemas.Exercise])
def read_exercises_by_muscle(muscle_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_exercises_by_muscle(db, muscle_id)

@app.post("/api/log", response_model=schemas.WorkoutSession)
def log_workout(session: schemas.WorkoutSessionCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_workout_session(db, session)

@app.get("/api/history", response_model=List[schemas.WorkoutSession])
def read_history(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_workout_history(db)

@app.get("/api/last-log/{exercise_id}", response_model=schemas.WorkoutSet)
def read_last_log(exercise_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    last_val = crud.get_last_workout_for_exercise(db, exercise_id)
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
