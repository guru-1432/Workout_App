from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    data = {
        "Chest": ["Declined press", "Inclined press", "Fly", "Flat press"],
        "Shoulder": ["Shoulder press", "Lateral fly", "Front raises"],
        "Biceps": ["Dumbbell curl", "Preacher curl", "Barbell curl"],
        "Triceps": ["Cable pulldown", "Overhead dips", "Single overhead dips"],
        "Lat": ["Lat pulldown", "Lat row"],
        "Core": ["Planks", "Russian twist", "Crunches"]
    }

    for muscle_name, exercises in data.items():
        muscle = db.query(models.Muscle).filter_by(name=muscle_name).first()
        if not muscle:
            muscle = models.Muscle(name=muscle_name)
            db.add(muscle)
            db.commit()
            db.refresh(muscle)
            print(f"Created Muscle: {muscle_name}")
        
        for ex_name in exercises:
            ex = db.query(models.Exercise).filter_by(name=ex_name, muscle_id=muscle.id).first()
            if not ex:
                ex = models.Exercise(name=ex_name, muscle_id=muscle.id)
                db.add(ex)
                print(f"  - Created Exercise: {ex_name}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_data()
