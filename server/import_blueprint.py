import zipfile
import os
import pandas as pd

from database import (
    SessionLocal,
    Institute, User, Employee, Student, Class, Room, ExamBranch
)


# ------------------------------------------------------------
# Helper: Convert Yes/No → Boolean
# ------------------------------------------------------------
def to_bool(value):
    if str(value).strip().lower() in ["yes", "true", "1"]:
        return True
    return False


# ------------------------------------------------------------
# Helper: Create user safely (no duplicates)
# ------------------------------------------------------------
def create_user(session, institute_id, full_name, email, role):
    existing = session.query(User).filter_by(email=email).first()
    if existing:
        return existing  # Reuse existing user

    user = User(
        institute_id=institute_id,
        full_name=full_name,
        email=email,
        role=role.upper(),
        password_hash=None
    )
    session.add(user)
    session.flush()  # Get auto-generated ID
    return user


# ------------------------------------------------------------
# Main Import Function
# ------------------------------------------------------------
def import_blueprint(zip_path):
    session = SessionLocal()

    # --------------------------------------------------------
    # 1. Extract ZIP file
    # --------------------------------------------------------
    extract_path = "extracted_blueprint"
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    print("✔ ZIP extracted:", extract_path)

    # --------------------------------------------------------
    # 2. Import INSTITUTE
    # --------------------------------------------------------
    institute_csv = os.path.join(extract_path, "institute.csv")
    df_inst = pd.read_csv(institute_csv)
    inst_row = df_inst.iloc[0]

    # Check if institute already exists
    existing_inst = session.query(Institute).filter_by(code=inst_row["code"]).first()

    if existing_inst:
        institute = existing_inst
        print(f"✔ Institute already exists: {institute.name} (ID={institute.id})")
    else:
        institute = Institute(
            name=inst_row["name"],
            logo_url=inst_row["logo_url"],
            code=inst_row["code"],
            address=inst_row["address"],
            timezone=inst_row["timezone"]
        )
        session.add(institute)
        session.commit()
        print(f"✔ Institute created: {institute.name} (ID={institute.id})")

    institute_id = institute.id

    # --------------------------------------------------------
    # 3. Import EMPLOYEES
    # --------------------------------------------------------
    employees_csv = os.path.join(extract_path, "employees.csv")
    df_emp = pd.read_csv(employees_csv)

    for _, row in df_emp.iterrows():
        user = create_user(
            session,
            institute_id,
            full_name=row["full_name"],
            email=row["email"],
            role=row["role"]
        )

        employee = Employee(
            user_id=user.id,
            institute_id=institute_id,
            department=row["department"],
            designation=row["designation"]
        )
        session.add(employee)

    print(f"✔ Employees imported: {len(df_emp)}")

    # --------------------------------------------------------
    # 4. Import STUDENTS
    # --------------------------------------------------------
    students_csv = os.path.join(extract_path, "students.csv")
    df_stu = pd.read_csv(students_csv)

    for _, row in df_stu.iterrows():
        user = create_user(
            session,
            institute_id,
            full_name=row["full_name"],
            email=row["email"],
            role="STUDENT"
        )

        student = Student(
            user_id=user.id,
            institute_id=institute_id,
            reg_no=row["reg_no"],
            roll_no=row["roll_no"],
            department=row["department"],
            semester=row["semester"],
            section=row["section"]
        )
        session.add(student)

    print(f"✔ Students imported: {len(df_stu)}")

    # --------------------------------------------------------
    # 5. Import CLASSES
    # --------------------------------------------------------
    classes_csv = os.path.join(extract_path, "classes.csv")
    df_cls = pd.read_csv(classes_csv)

    for _, row in df_cls.iterrows():
        cls = Class(
            institute_id=institute_id,
            department=row["department"],
            semester=row["semester"],
            section=row["section"],
            capacity=row["capacity"]
        )
        session.add(cls)

    print(f"✔ Classes imported: {len(df_cls)}")

    # --------------------------------------------------------
    # 6. Import ROOMS
    # --------------------------------------------------------
    rooms_csv = os.path.join(extract_path, "rooms.csv")
    df_rooms = pd.read_csv(rooms_csv)

    for _, row in df_rooms.iterrows():
        room = Room(
            institute_id=institute_id,
            name=row["name"],
            type=row["type"],
            capacity=row["capacity"],
            systems_count=row.get("systems_count", 0),
            has_projector=to_bool(row.get("has_projector"))
        )
        session.add(room)

    print(f"✔ Rooms imported: {len(df_rooms)}")

    # --------------------------------------------------------
    # 7. Import EXAM BRANCHES
    # --------------------------------------------------------
    exam_branch_csv = os.path.join(extract_path, "examination_branch.csv")
    df_exb = pd.read_csv(exam_branch_csv)

    for _, row in df_exb.iterrows():
        branch = ExamBranch(
            institute_id=institute_id,
            branch_name=row["branch_name"],
            manager_email=row["manager_email"]
        )
        session.add(branch)

    print(f"✔ Exam Branches imported: {len(df_exb)}")

    # --------------------------------------------------------
    # Final Commit
    # --------------------------------------------------------
    session.commit()
    session.close()

    print("\n🎉 ALL CSV FILES IMPORTED SUCCESSFULLY!")
    print("Institute onboarding completed!")


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    zip_file = "institute_data.zip"     # change if needed
    import_blueprint(zip_file)
