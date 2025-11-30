# ============================================================
#  ATTENDANCE MODULE ROUTES - FASTAPI
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from sqlalchemy.orm import Session
from database import Attendance, Subject, Student, Employee, FacultySubject
from database import SessionLocal

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

# ------------------------------------------------------------
# Dependency: DB Session
# ------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------
# 1. Pydantic Models
# ------------------------------------------------------------
class AttendanceInput(BaseModel):
    student_id: int
    subject_id: int
    date: str
    status: str      # PRESENT / ABSENT / LATE / EXCUSED
    marked_by: int   # faculty_id


# ------------------------------------------------------------
# 2. Mark Attendance (Create/Update)
# ------------------------------------------------------------
@router.post("/mark")
def mark_attendance(data: AttendanceInput, db: Session = Depends(get_db)):

    # Validations
    student = db.query(Student).filter_by(id=data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    faculty = db.query(Employee).filter_by(id=data.marked_by).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    subject = db.query(Subject).filter_by(id=data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Prevent duplicate attendance for same student/date/subject
    existing_att = db.query(Attendance).filter_by(
        student_id=data.student_id,
        subject_id=data.subject_id,
        date=data.date
    ).first()

    if existing_att:
        existing_att.status = data.status
        db.commit()
        return {"message": "Attendance updated successfully"}

    # Insert new attendance row
    new_att = Attendance(
        student_id=data.student_id,
        subject_id=data.subject_id,
        date=data.date,
        status=data.status.upper(),
        marked_by=data.marked_by,
    )

    db.add(new_att)
    db.commit()

    return {"message": "Attendance marked successfully"}


# ------------------------------------------------------------
# 3. Get Class Attendance for a Subject & Date
# ------------------------------------------------------------
@router.get("/class/{subject_id}/{date}")
def get_class_attendance(subject_id: int, date: str, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter_by(subject_id=subject_id, date=date).all()

    return {
        "subject_id": subject_id,
        "date": date,
        "total_records": len(records),
        "attendance": records
    }


# ------------------------------------------------------------
# 4. Get Student Attendance Summary
# ------------------------------------------------------------
@router.get("/student/{student_id}")
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter_by(student_id=student_id).all()

    present = len([r for r in records if r.status == "PRESENT"])
    total = len(records)
    percentage = round((present / total) * 100, 2) if total > 0 else 0

    return {
        "student_id": student_id,
        "total_classes": total,
        "present": present,
        "attendance_percentage": percentage,
        "records": records
    }


# ------------------------------------------------------------
# 5. Get Attendance for a Subject (Full History)
# ------------------------------------------------------------
@router.get("/subject/{subject_id}")
def subject_attendance_history(subject_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter_by(subject_id=subject_id).all()

    return {
        "subject_id": subject_id,
        "total_records": len(records),
        "records": records
    }


# ------------------------------------------------------------
# 6. Get Subjects Assigned to Faculty (Faculty Dashboard)
# ------------------------------------------------------------
@router.get("/faculty/{faculty_id}/subjects")
def get_faculty_subjects(faculty_id: int, db: Session = Depends(get_db)):
    mappings = db.query(FacultySubject).filter_by(faculty_id=faculty_id).all()

    subjects = []
    for m in mappings:
        sub = db.query(Subject).filter_by(id=m.subject_id).first()
        if sub:
            subjects.append({
                "subject_id": sub.id,
                "subject_name": sub.name,
                "subject_code": sub.code,
                "class_id": m.class_id
            })

    return {
        "faculty_id": faculty_id,
        "subjects": subjects
    }
