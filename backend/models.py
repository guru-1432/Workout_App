from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)

    sessions = relationship("WorkoutSession", back_populates="user")


class Muscle(Base):
    __tablename__ = "muscles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    exercises = relationship("Exercise", back_populates="muscle")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    muscle_id = Column(Integer, ForeignKey("muscles.id"))

    muscle = relationship("Muscle", back_populates="exercises")
    logs = relationship("WorkoutSet", back_populates="exercise")

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    # Could imply a focus muscle, but allowing flexibility is better.
    # User said: "When I log will select which muscle group I will train today"
    # So maybe we store the primary muscle group for the session, or just tags.
    # Let's keep it simple for now. 

    sets = relationship("WorkoutSet", back_populates="session")
    user = relationship("User", back_populates="sessions")

class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    weight = Column(Integer)
    reps = Column(Integer)

    session = relationship("WorkoutSession", back_populates="sets")
    exercise = relationship("Exercise", back_populates="logs")
