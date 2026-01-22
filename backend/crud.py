from sqlalchemy.orm import Session, joinedload
import models, schemas
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: models.User, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    # Invalidate reset token if present
    user.reset_token = None 
    db.commit()
    db.refresh(user)
    return user

def set_reset_token(db: Session, user: models.User, token: str):
    user.reset_token = token
    db.commit()
    db.refresh(user)

def get_user_by_reset_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.reset_token == token).first()


def get_muscles(db: Session):
    return db.query(models.Muscle).all()

def create_muscle(db: Session, muscle: schemas.MuscleCreate):
    db_muscle = models.Muscle(name=muscle.name)
    db.add(db_muscle)
    db.commit()
    db.refresh(db_muscle)
    return db_muscle

def get_exercises_by_muscle(db: Session, muscle_id: int):
    return db.query(models.Exercise).filter(models.Exercise.muscle_id == muscle_id).all()

def get_all_exercises(db: Session):
    return db.query(models.Exercise).all()

def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(name=exercise.name, muscle_id=exercise.muscle_id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def create_workout_session(db: Session, session: schemas.WorkoutSessionCreate, user_id: int):
    db_session = models.WorkoutSession(date=session.date, user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    for s in session.sets:
        db_set = models.WorkoutSet(
            session_id=db_session.id,
            exercise_id=s.exercise_id,
            weight=s.weight,
            reps=s.reps
        )
        db.add(db_set)
    
    db.commit()
    db.refresh(db_session)
    return db_session

def get_workout_history(db: Session, user_id: int):
    return db.query(models.WorkoutSession).filter(models.WorkoutSession.user_id == user_id).options(
        joinedload(models.WorkoutSession.sets).joinedload(models.WorkoutSet.exercise)
    ).order_by(models.WorkoutSession.date.desc()).all()

def get_last_workout_for_exercise(db: Session, exercise_id: int, user_id: int):
    # Get the last set for this exercise
    return db.query(models.WorkoutSet).join(models.WorkoutSession)\
        .filter(models.WorkoutSet.exercise_id == exercise_id)\
        .filter(models.WorkoutSession.user_id == user_id)\
        .order_by(models.WorkoutSession.date.desc()).first()

def delete_muscle(db: Session, muscle_id: int):
    muscle = db.query(models.Muscle).filter(models.Muscle.id == muscle_id).first()
    if muscle:
        db.delete(muscle)
        db.commit()
    return muscle

def delete_exercise(db: Session, exercise_id: int):
    ex = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if ex:
        db.delete(ex)
        db.commit()
    return ex


