import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Date, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import roles_required
from dotenv import load_dotenv
import pandas as pd
from datetime import date, timedelta
import helpers

load_dotenv()
ADMIN_ROLE = "Admin"
SERVICE_ADMIN_ROLE = "Service Admin"
TEACHER_ROLE = "Teacher"
GUARDIAN_ROLE = "Guardian"


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# DB Models-------------------------------------------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)  # Admin, Teacher, Guardian
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    branch = relationship("Branch", back_populates="user")
    is_active: Mapped[bool] = mapped_column(default=True)
    has_lesson_schedule_option_access: Mapped[bool] = mapped_column(default=True)
    has_attendance_option_access: Mapped[bool] = mapped_column(default=True)
    has_accounts_option_access: Mapped[bool] = mapped_column(default=True)
    has_results_option_access: Mapped[bool] = mapped_column(default=True)
    has_qr_code_access: Mapped[bool] = mapped_column(default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Branch(db.Model):
    __tablename__ = "branches"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    office_phone: Mapped[str] = mapped_column()
    head_teacher_phone: Mapped[str] = mapped_column()
    user = relationship("User", back_populates="branch")


class Class(db.Model):
    __tablename__ = "classes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    lesson_schedules = relationship("Curriculum", back_populates="class_")


class Subject(db.Model):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    lesson_schedules = relationship("Curriculum", back_populates="subject")


class Curriculum(db.Model):
    __tablename__ = "curriculum"
    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    topic: Mapped[str] = mapped_column()

    class_ = relationship("Class", back_populates="lesson_schedules")
    subject = relationship("Subject", back_populates="lesson_schedules")


class Video(db.Model):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(nullable=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))


# End of DB Models------------------------------------------------------------------------------------------------------

with app.app_context():
    db.create_all()

    if not db.session.execute(db.select(User).where(User.username == 'al-aqsa-sharif')).scalar():
        branch = Branch(name="Netrakona", office_phone="017222929299", head_teacher_phone="01828282888")
        db.session.add(branch)
        db.session.commit()

        admin = User(username='al-aqsa-sharif', branch_id=branch.id, role=ADMIN_ROLE, school_id=101)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()


# Routes -------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.session.execute(
            db.select(User).where((User.username == username) & (User.is_active == True))).scalar()

        if user and user.check_password(password):
            login_user(user, duration=timedelta(hours=3))
            return helpers.redirect_dashboard(user.role)

        flash('Invalid username or password', 'danger')
        return redirect(url_for("login"))

    return render_template('login.html')


# Dashboard Routes -----------------------------------------------------------------------------------------------------
@app.route('/admin-dashboard')
@login_required
@roles_required(ADMIN_ROLE)
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')


@app.route('/service-admin-dashboard')
@login_required
@roles_required(SERVICE_ADMIN_ROLE)
def service_admin_dashboard():
    return render_template('service-admin_dashboard.html')


@app.route('/teacher-dashboard')
@login_required
@roles_required(TEACHER_ROLE)
def teacher_dashboard():
    return render_template('teacher_dashboard.html')


@app.route('/guardian-dashboard')
@login_required
@roles_required(GUARDIAN_ROLE)
def guardian_dashboard():
    return render_template('guardian/guardian_dashboard.html')


# Options --------------------------------------------------------------------------------------------------------------
@app.route("/lesson-schedule")
@login_required
def lesson_schedule():
    return render_template("admin/lesson_schedule.html")


@app.route("/attendance")
@login_required
def attendance():
    return render_template("attendance.html")


@app.route("/accounts")
@login_required
def accounts():
    return render_template("accounts.html")


@app.route("/result")
@login_required
def result():
    return render_template("result.html")


@app.route("/qr-code-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def qr_code_management():
    return render_template("admin/qr_code_management.html")


@app.route("/qr-scanner")
@login_required
def qr_scanner():
    return render_template("qr_scanner.html")


@app.route("/tutorial-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def tutorial_management():
    return render_template("admin/tutorial_management.html")


@app.route("/admin-user-management")
def admin_user_management():
    return render_template("admin/user_management.html")


@app.route("/call-services")
@login_required
def call_services():
    return render_template("call_service.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# APIs -----------------------------------------------------------------------------------------------------------------
@app.route("/api/upload_curriculum", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_curriculum():
    class_name = request.form["class_name"]
    class_obj = db.session.execute(db.select(Class).where(Class.name == class_name)).scalar()

    subject = request.form["subject"]
    subject_obj = db.session.execute(db.select(Subject).where(Subject.name == subject)).scalar()

    file = request.files["excel_file"]

    # read excel
    df = pd.read_csv(file)

    print(df)
    for index, row in df.iterrows():
        curriculum_date = str(row["Date"])
        day, month, year = curriculum_date.split("/")
        date_obj = date(day=int(day), month=int(month), year=int(year))

        # Deletes Previous Data
        previous_records = db.session.execute(db.select(Curriculum).where(
            (Curriculum.class_id == class_obj.id) & (Curriculum.subject_id == subject_obj.id))).scalars().all()
        for previous_record in previous_records:
            db.session.delete(previous_record)

        topic = row["Topic"]
        curriculum_obj = Curriculum(class_id=class_obj.id, subject_id=subject_obj.id, date=date_obj, topic=topic)
        db.session.add(curriculum_obj)
    db.session.commit()

    return redirect(url_for("lesson_schedule"))


@app.route("/api/search-curriculum", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_curriculum():
    data = request.json
    class_name = data["class"]
    class_obj = db.session.execute(db.select(Class).where(Class.name == class_name)).scalar()
    lesson_schedule_date = data["date"]
    year, month, day = lesson_schedule_date.split("-")
    date_obj = date(day=int(day), month=int(month), year=int(year))

    result = db.session.execute(
        db.select(Curriculum).where(Curriculum.class_id == class_obj.id and Curriculum.date == date_obj))

    rows = result.scalars().all()

    results = []

    for r in rows:
        results.append({
            "id": r.id,
            "class": r.class_.name,
            "subject": r.subject.name,
            "date": r.date,
            "topic": r.topic,
        })

    return {"data": results}


@app.route("/api/update-curriculum", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def update_curriculum():
    data = request.json

    lesson_schedule = db.session.get(Curriculum, int(data["id"]))
    lesson_schedule.topic = data["topic"]
    db.session.commit()

    return {"status": "success"}


@app.route("/api/upload-videos", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_videos():
    class_name = request.form["class_name"]
    class_obj = db.session.execute(db.select(Class).where(Class.name == class_name)).scalar()

    file = request.files["excel_file"]

    # read excel
    df = pd.read_csv(file)

    for index, row in df.iterrows():
        video_id = str(row["ID"])
        video_link = row["Link"]
        video_obj = Video(id=video_id, class_id=class_obj.id, link=video_link)
        db.session.add(video_obj)
        db.session.commit()

    return redirect(url_for("tutorial_management"))


@app.route("/api/get-video", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def get_video():
    data = request.json
    video_id = data["id"]

    video = db.session.get(Video, video_id)

    if not video:
        return jsonify({"success": False})

    return jsonify({
        "success": True,
        "video": {
            "id": video.id,
            "video_link": video.link
        }
    })


@app.route("/api/update-video", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def update_video():
    data = request.json

    video = db.session.get(Video, data["video_id"])
    video.link = data["video_link"]

    db.session.commit()

    return jsonify({"success": True})


@app.route("/api/add-user", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def add_user():
    data = request.json

    # Extract fields
    school_id = data.get("id")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    branch = data.get("branch")

    # Options (lesson_schedule, attendance, accounts, result, qr_scanner)
    lesson_schedule_access = data.get("lesson_schedule", False)
    attendance_access = data.get("attendance", False)
    accounts_access = data.get("accounts", False)
    result_access = data.get("result", False)
    qr_code_access = data.get("qr_code", False)

    # Simple validation
    if not school_id or not username or not password or not role or branch == "Select Branch":
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    branch = db.session.execute(db.select(Branch).where(Branch.name == branch)).scalar()
    # Add user
    user = User(
        school_id=school_id,
        username=username,
        role=role,
        branch_id=branch.id,
        has_lesson_schedule_option_access=lesson_schedule_access,
        has_attendance_option_access=attendance_access,
        has_accounts_option_access=accounts_access,
        has_results_option_access=result_access,
        has_qr_code_access=qr_code_access

    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/search-users", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def search_users():
    filters = request.json or {}
    branch_name = filters.get("branch")
    role = filters.get("role")
    school_id = filters.get("id")  # coming from the client

    stmt = db.select(User)

    # filter by branch if provided
    if branch_name:
        # find branch first
        branch_obj = db.session.execute(
            db.select(Branch).where(Branch.name == branch_name)
        ).scalar_one_or_none()

        # if branch not found, return empty result
        if branch_obj is None:
            return jsonify({"users": []})

        stmt = stmt.where(User.branch_id == branch_obj.id)

    # filter by role if provided
    if role:
        stmt = stmt.where(User.role == role)

    # filter by school_id if provided
    if school_id:
        try:
            school_id_int = int(school_id)
            stmt = stmt.where(User.school_id == school_id_int)
        except ValueError:
            # invalid numeric id; return empty result or ignore
            return jsonify({"users": []})

    # execute query
    users = db.session.execute(stmt).scalars().all()

    # serialize cleanly
    def serialize_user(u):
        return {
            "db_id": u.id,
            "id": u.school_id,  # adjust field names to your model
            "username": u.username,
            "role": u.role,
            "branch": getattr(u.branch, "name", None) if getattr(u, "branch", None) else None,
            # example option fields; rename if different in your model
            "lesson_schedule": u.has_lesson_schedule_option_access,
            "attendance": u.has_attendance_option_access,
            "accounts": u.has_accounts_option_access,
            "result": u.has_results_option_access,
            "qr_code": u.has_qr_code_access,
        }

    users_serialized = [serialize_user(u) for u in users]

    return jsonify({"users": users_serialized})


@app.route("/api/update-user", methods=["PATCH"])
@login_required
@roles_required(ADMIN_ROLE)
def update_user():
    data = request.json

    # Extract fields
    db_id = data.get("db_id")
    school_id = data.get("id")
    username = data.get("username")
    branch = data.get("branch")

    # Options (lesson_schedule, attendance, accounts, result, qr_scanner)
    lesson_schedule_access = data.get("lesson_schedule", False)
    attendance_access = data.get("attendance", False)
    accounts_access = data.get("accounts", False)
    result_access = data.get("result", False)
    qr_code_access = data.get("qr_code", False)

    # Simple validation
    if not school_id or not username:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    branch_obj = db.session.execute(db.select(Branch).where(Branch.name == branch)).scalar()

    # Update user
    user = db.session.get(User, db_id)
    user.school_id = school_id
    user.username = username
    user.branch_id = branch_obj.id
    user.has_lesson_schedule_option_access = lesson_schedule_access
    user.has_attendance_option_access = attendance_access
    user.has_accounts_option_access = accounts_access
    user.has_results_option_access = result_access
    user.has_qr_code_access = qr_code_access

    db.session.commit()
    return jsonify({"success": True})


@app.route("/api/delete-user/<id>", methods=["DELETE"])
@login_required
@roles_required(ADMIN_ROLE)
def delete_user(id):
    try:
        user = db.session.get(User, id)
        db.session.delete(user)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route('/api/change-password', methods=["PATCH"])
@login_required
@roles_required(ADMIN_ROLE)
def change_password():
    data = request.json
    id = data["id"]
    password = data["password"]
    if current_user.role != ADMIN_ROLE:
        abort(403)
    user = db.session.get(User, id)
    user.set_password(password)
    db.session.commit()
    return {"success": True}


# Others ---------------------------------------------------------------------------------------------------------------
@app.route("/video/<int:video_id>")
@login_required
def show_video(video_id):
    video = db.get_or_404(Video, video_id)

    return render_template(
        "video.html",
        video_link=video.link
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
