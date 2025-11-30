# ============================================================
#  INTEGRATED ACADEMIC & EXAM MANAGEMENT SYSTEM - DATABASE FILE
# ============================================================

import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean,
    ForeignKey, Text, TIMESTAMP
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# ------------------------------------------------------------
# 1. Load Environment Variables
# ------------------------------------------------------------
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ------------------------------------------------------------
# 2. Database Connection
# ------------------------------------------------------------
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ------------------------------------------------------------
# 3. MODELS
# ------------------------------------------------------------

class Institute(Base):
    __tablename__ = "institutes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    logo_url = Column(Text)
    code = Column(String(50), unique=True, nullable=False)
    address = Column(Text)
    timezone = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    users = relationship("User", back_populates="institute")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text)
    role = Column(String(50), nullable=False)   # ADMIN / STUDENT / FACULTY / EXAM_MANAGER
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    institute = relationship("Institute", back_populates="users")
    student = relationship("Student", uselist=False, back_populates="user")
    employee = relationship("Employee", uselist=False, back_populates="user")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    department = Column(String(255))
    designation = Column(String(255))

    user = relationship("User", back_populates="employee")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    reg_no = Column(String(100), unique=True, nullable=False)
    roll_no = Column(String(100))
    department = Column(String(255))
    semester = Column(Integer)
    section = Column(String(50))

    user = relationship("User", back_populates="student")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    department = Column(String(255), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)   # CLASS / LAB / SEMINAR
    capacity = Column(Integer, nullable=False)
    systems_count = Column(Integer, default=0)
    has_projector = Column(Boolean, default=False)


class ExamBranch(Base):
    __tablename__ = "exam_branches"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.id", ondelete="CASCADE"))
    branch_name = Column(String(255), nullable=False)
    manager_email = Column(String(255), nullable=False)


class BlueprintUpload(Base):
    __tablename__ = "blueprint_uploads"

    id = Column(Integer, primary_key=True)
    institute_id = Column(Integer, ForeignKey("institutes.id"))
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    zip_path = Column(Text)
    status = Column(String(50), default="PENDING")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ------------------------------------------------------------
# 4. Create All Tables
# ------------------------------------------------------------
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✔ Database tables created successfully.")


# Run directly
if __name__ == "__main__":
    init_db()
