from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import (
    SessionLocal,
    Institute, User, Employee, Student, Class,
    Room, ExamBranch,Attendance,Subject,FacultySubject
)

router = APIRouter(prefix="/debug", tags=["Debug"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/all")
def view_all_tables(db: Session = Depends(get_db)):
    return {
        "institutes": db.query(Institute).all(),
        "users": db.query(User).all(),
        "employees": db.query(Employee).all(),
        "students": db.query(Student).all(),
        "classes": db.query(Class).all(),
        "rooms": db.query(Room).all(),
        "exam_branches": db.query(ExamBranch).all(),
        "Attendance": db.query(Attendance).all(),
        "FacultySubject": db.query(FacultySubject).all(),
        "Subject": db.query(Subject).all()

        
    }
