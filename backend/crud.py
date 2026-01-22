from sqlalchemy.orm import Session, joinedload
import models, schemas
from datetime import datetime

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

def create_workout_session(db: Session, session: schemas.WorkoutSessionCreate):
    db_session = models.WorkoutSession(date=session.date)
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

def get_workout_history(db: Session):
    return db.query(models.WorkoutSession).options(
        joinedload(models.WorkoutSession.sets).joinedload(models.WorkoutSet.exercise)
    ).order_by(models.WorkoutSession.date.desc()).all()

def get_last_workout_for_exercise(db: Session, exercise_id: int):
    # Get the last set for this exercise
    return db.query(models.WorkoutSet).join(models.WorkoutSession).filter(models.WorkoutSet.exercise_id == exercise_id).order_by(models.WorkoutSession.date.desc()).first()

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


