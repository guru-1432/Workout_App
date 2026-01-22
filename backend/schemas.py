from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MuscleBase(BaseModel):
    name: str

class MuscleCreate(MuscleBase):
    pass

class Muscle(MuscleBase):
    id: int
    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    muscle_id: int

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    class Config:
        from_attributes = True

class WorkoutSetBase(BaseModel):
    exercise_id: int
    weight: float
    reps: int

class WorkoutSetCreate(WorkoutSetBase):
    pass

class WorkoutSet(WorkoutSetBase):
    id: int
    session_id: int
    exercise: Optional['Exercise'] = None
    class Config:
        from_attributes = True
        
class WorkoutSessionBase(BaseModel):
    date: datetime

class WorkoutSessionCreate(WorkoutSessionBase):
    sets: List[WorkoutSetCreate]

class WorkoutSession(WorkoutSessionBase):
    id: int
    sets: List[WorkoutSet] = []
    class Config:
        from_attributes = True

class ExerciseWithMuscle(Exercise):
    muscle: Muscle
