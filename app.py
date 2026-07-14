import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Date, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import roles_required
from dotenv import load_dotenv
import pandas as pd
from datetime import date, timedelta, datetime
import helpers
from zoneinfo import ZoneInfo

load_dotenv()

ADMIN_ROLE = "Admin"
SERVICE_ADMIN_ROLE = "Service Admin"
TEACHER_ROLE = "Teacher"
STUDENT_ROLE = "Student"

CLASS_MAP = {
    1: "Play",
    2: "Nursery",
    3: "One",
    4: "Two",
    5: "Three",
    6: "Four",
    7: "Five",
}


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


class Curriculum(db.Model):
    __tablename__ = "curriculum"
    id: Mapped[int] = mapped_column(primary_key=True)
    class_name: Mapped[str] = mapped_column()
    subject_name: Mapped[str] = mapped_column()
    date: Mapped[date] = mapped_column(Date)
    topic: Mapped[str] = mapped_column()


class Video(db.Model):
    __tablename__ = "videos"
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column()


class AttendanceRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    month: Mapped[str] = mapped_column()
    student_id: Mapped[int] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    d1: Mapped[str] = mapped_column(nullable=True)
    d2: Mapped[str] = mapped_column(nullable=True)
    d3: Mapped[str] = mapped_column(nullable=True)
    d4: Mapped[str] = mapped_column(nullable=True)
    d5: Mapped[str] = mapped_column(nullable=True)
    d6: Mapped[str] = mapped_column(nullable=True)
    d7: Mapped[str] = mapped_column(nullable=True)
    d8: Mapped[str] = mapped_column(nullable=True)
    d9: Mapped[str] = mapped_column(nullable=True)
    d10: Mapped[str] = mapped_column(nullable=True)
    d11: Mapped[str] = mapped_column(nullable=True)
    d12: Mapped[str] = mapped_column(nullable=True)
    d13: Mapped[str] = mapped_column(nullable=True)
    d14: Mapped[str] = mapped_column(nullable=True)
    d15: Mapped[str] = mapped_column(nullable=True)
    d16: Mapped[str] = mapped_column(nullable=True)
    d17: Mapped[str] = mapped_column(nullable=True)
    d18: Mapped[str] = mapped_column(nullable=True)
    d19: Mapped[str] = mapped_column(nullable=True)
    d20: Mapped[str] = mapped_column(nullable=True)
    d21: Mapped[str] = mapped_column(nullable=True)
    d22: Mapped[str] = mapped_column(nullable=True)
    d23: Mapped[str] = mapped_column(nullable=True)
    d24: Mapped[str] = mapped_column(nullable=True)
    d25: Mapped[str] = mapped_column(nullable=True)
    d26: Mapped[str] = mapped_column(nullable=True)
    d27: Mapped[str] = mapped_column(nullable=True)
    d28: Mapped[str] = mapped_column(nullable=True)
    d29: Mapped[str] = mapped_column(nullable=True)
    d30: Mapped[str] = mapped_column(nullable=True)
    d31: Mapped[str] = mapped_column(nullable=True)


class AccountsRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    student_id: Mapped[int] = mapped_column()
    student_name: Mapped[str] = mapped_column()
    january: Mapped[float] = mapped_column(nullable=True)
    february: Mapped[float] = mapped_column(nullable=True)
    march: Mapped[float] = mapped_column(nullable=True)
    april: Mapped[float] = mapped_column(nullable=True)
    may: Mapped[float] = mapped_column(nullable=True)
    june: Mapped[float] = mapped_column(nullable=True)
    july: Mapped[float] = mapped_column(nullable=True)
    august: Mapped[float] = mapped_column(nullable=True)
    september: Mapped[float] = mapped_column(nullable=True)
    october: Mapped[float] = mapped_column(nullable=True)
    november: Mapped[float] = mapped_column(nullable=True)
    december: Mapped[float] = mapped_column(nullable=True)
    due: Mapped[float] = mapped_column(nullable=True)


class SemesterResultRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column(nullable=False)
    exam_name: Mapped[str] = mapped_column(nullable=False)
    student_id: Mapped[int] = mapped_column(nullable=False)
    student_name: Mapped[str] = mapped_column(nullable=True)
    merit: Mapped[int] = mapped_column(nullable=True)
    arabic: Mapped[float] = mapped_column(nullable=True)
    quran: Mapped[float] = mapped_column(nullable=True)
    bengali: Mapped[float] = mapped_column(nullable=True)
    english: Mapped[float] = mapped_column(nullable=True)
    math: Mapped[float] = mapped_column(nullable=True)
    science: Mapped[float] = mapped_column(nullable=True)
    bgs: Mapped[float] = mapped_column(nullable=True)
    aqaid_and_fiqh: Mapped[float] = mapped_column(nullable=True)
    class_test: Mapped[float] = mapped_column(nullable=True)
    presence: Mapped[float] = mapped_column(nullable=True)
    total: Mapped[float] = mapped_column(nullable=True)
    letter_grade: Mapped[str] = mapped_column(nullable=True)


class ClassTestResultRecord(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column(nullable=False)
    class_name: Mapped[str] = mapped_column(nullable=False)
    month: Mapped[str] = mapped_column(nullable=False)
    student_id: Mapped[int] = mapped_column(nullable=False)
    student_name: Mapped[str] = mapped_column()
    arabic: Mapped[float] = mapped_column(nullable=True)
    quran: Mapped[float] = mapped_column(nullable=True)
    bengali: Mapped[float] = mapped_column(nullable=True)
    english: Mapped[float] = mapped_column(nullable=True)
    math: Mapped[float] = mapped_column(nullable=True)
    science: Mapped[float] = mapped_column(nullable=True)
    aqaid_and_fiqh: Mapped[float] = mapped_column(nullable=True)
    bgs: Mapped[float] = mapped_column(nullable=True)
    total: Mapped[float] = mapped_column(nullable=True)


class Notice(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    notice_link: Mapped[str] = mapped_column()
    branch: Mapped[str] = mapped_column()


class LogInfo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    login_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))


class PhoneNumber(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_name: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    comment: Mapped[str] = mapped_column()
    comment_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))

    reply = relationship("CommentReply", back_populates="comment", uselist=False)


class CommentReply(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    replier: Mapped[str] = mapped_column()
    comment_id: Mapped[int] = mapped_column(ForeignKey(Comment.id))
    reply_txt: Mapped[str] = mapped_column()
    reply_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Dhaka")))

    comment = relationship("Comment", back_populates="reply")



# End of DB Models------------------------------------------------------------------------------------------------------

with app.app_context():
    db.create_all()

    if not db.session.execute(db.select(User).where(User.username == 'al-aqsa-sharif')).scalar():
        branch = Branch(name="Netrakona", office_phone="01811114400", head_teacher_phone="01710500660")
        db.session.add(branch)
        branch_1 = Branch(name="Purbadhala", office_phone="01811114400", head_teacher_phone="01710500660")
        db.session.add(branch_1)
        branch_2 = Branch(name="Kalmakanda", office_phone="01811114400", head_teacher_phone="01710500660")
        db.session.add(branch_2)
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

        user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if user and user.check_password(password):
            log = LogInfo(username=user.username)
            db.session.add(log)
            db.session.commit()
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
    return render_template('service_admin/service-admin_dashboard.html')


@app.route('/teacher-dashboard')
@login_required
@roles_required(TEACHER_ROLE)
def teacher_dashboard():
    return render_template('teacher/teacher_dashboard.html')


@app.route('/student-dashboard')
@login_required
@roles_required(STUDENT_ROLE)
def student_dashboard():
    class_code = int(str(current_user.school_id)[0])
    return render_template('student/student_dashboard.html', class_code=class_code)


# Options --------------------------------------------------------------------------------------------------------------
@app.route("/lesson-schedule")
@login_required
def lesson_schedule():
    return render_template("lesson_schedule.html")


@app.route("/student-lesson-schedule")
@login_required
def student_lesson_schedule():
    student_id = str(request.args.get("student_id"))
    student_class = CLASS_MAP[int(student_id[:1])]
    return render_template("student/lesson_schedule.html", student_class=student_class)


@app.route("/student-lesson-syllabus")
@login_required
def student_lesson_syllabus():
    student_id = str(request.args.get("student_id"))
    student_class = CLASS_MAP[int(student_id[:1])]
    return render_template("student/student_lesson_syllabus.html", student_class=student_class)


@app.route("/lesson-syllabus")
@login_required
def lesson_syllabus():
    return render_template("lesson_syllabus.html")


@app.route("/attendance")
@login_required
def attendance():
    return render_template("attendance.html", year=datetime.now().strftime("%Y"))


@app.route("/student-attendance")
@login_required
def student_attendance():
    student_id = str(request.args.get("student_id"))
    student_class = CLASS_MAP[int(student_id[:1])]
    return render_template("student/attendance.html", student_class=student_class, year=datetime.now().strftime("%Y"))


@app.route("/accounts")
@login_required
def accounts():
    return render_template("accounts.html")


@app.route("/student-accounts")
@login_required
def student_accounts():
    student_id = str(request.args.get("student_id"))
    student_class = CLASS_MAP[int(student_id[:1])]
    return render_template("student/student_accounts.html", student_class=student_class)


@app.route("/result")
@login_required
def result():
    return render_template("result.html")


@app.route("/student-result")
@login_required
def student_result():
    return render_template("student/student_result.html")


@app.route("/result/semester-assessment")
@login_required
def semester_assessment():
    return render_template("semester_assessment.html", year=datetime.now().strftime("%Y"))


@app.route("/student-result/semester-assessment")
@login_required
def student_semester_assessment():
    student_class = CLASS_MAP[int(str(current_user.school_id)[:1])]
    return render_template("student/semester_assessment.html", student_class=student_class,
                           year=datetime.now().strftime("%Y"))


@app.route("/result/class-assessment")
@login_required
def class_assessment():
    return render_template("class_assessment.html", year=datetime.now().strftime("%Y"))


@app.route("/student-result/class-assessment")
@login_required
def student_class_assessment():
    student_class = CLASS_MAP[int(str(current_user.school_id)[:1])]
    records = db.session.query(ClassTestResultRecord).all()
    uploaded_months = []
    for record in records:
        if record.month not in uploaded_months:
            uploaded_months.append(record.month)
    return render_template("student/class_assessment.html", student_class=student_class,
                           year=datetime.now().strftime("%Y"), months=uploaded_months)


@app.route("/qr-code-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def qr_code_management():
    return render_template("admin/qr_code_management.html")


@app.route("/qr-scanner")
@login_required
def qr_scanner():
    return render_template("qr_scanner.html")


@app.route("/qr-code-management/tutorial-management")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def tutorial_management():
    return render_template("admin/tutorial_management.html")


@app.route("/admin-user-management")
@login_required
@roles_required(ADMIN_ROLE)
def admin_user_management():
    return render_template("admin/user_management.html")


@app.route("/admin-user-management/service-admin")
@login_required
@roles_required(ADMIN_ROLE)
def service_admin_user_management():
    return render_template("admin/service_admin_user_management.html")


@app.route("/admin-user-management/teacher")
@login_required
@roles_required(ADMIN_ROLE)
def teacher_user_management():
    return render_template("admin/teacher_user_management.html")


@app.route("/admin-user-management/student")
@login_required
@roles_required(ADMIN_ROLE)
def student_user_management():
    return render_template("admin/student_user_management.html")


@app.route("/notice-board-management")
@login_required
def notice_board_management():
    notice_folder = os.path.join(
        app.static_folder,
        "img",
        "notices",
        current_user.branch.name
    )

    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")

    images = []

    for file in os.listdir(notice_folder):
        if file.lower().endswith(image_extensions):
            images.append(
                url_for(
                    "static",
                    filename=f"img/notices/{current_user.branch.name}/{file}"
                )
            )


    return render_template("notice_board_management.html", srcs=images[::-1])


@app.route("/log-info")
@login_required
@roles_required(ADMIN_ROLE)
def log_info():
    log_infos = db.session.query(LogInfo).all()[::-1]
    return render_template("admin/log_info.html", log_infos=log_infos)


@app.route("/submitted-comments")
@login_required
@roles_required(ADMIN_ROLE)
def submitted_comments():
    comments = db.session.query(Comment).all()[::-1]
    return render_template("admin/comments.html", comments=comments)


@app.route("/comment")
@login_required
def student_comment():
    comments = db.session.query(Comment).filter_by(username=current_user.username).all()
    return render_template("student/comments.html", comments=comments)


@app.route("/call-services")
@login_required
def call_services():
    phone_numbers = db.session.query(PhoneNumber).filter_by(branch_name=current_user.branch.name).all()
    return render_template("call_service.html", phone_numbers=phone_numbers)


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


# APIs -----------------------------------------------------------------------------------------------------------------
@app.route("/upload-curriculum", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_curriculum():
    try:
        class_name = request.form["class_name"].strip()
        subject_name = request.form["subject_name"].strip()
        file = request.files.get("excel_file")

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        required_columns = {"Date", "Topic"}
        if not required_columns.issubset(df.columns):
            raise ValueError("Missing required columns")

        records = []

        for _, row in df.iterrows():
            topic = row["Topic"]

            if pd.isna(topic):
                continue

            curriculum_date = pd.to_datetime(row["Date"], errors="coerce")
            if pd.isna(curriculum_date):
                continue

            records.append(Curriculum(
                class_name=class_name,
                subject_name=subject_name,
                date=curriculum_date,
                topic=str(topic)
            ))

        # Delete only AFTER validation
        db.session.query(Curriculum).filter_by(
            class_name=class_name,
            subject_name=subject_name
        ).delete()

        db.session.bulk_save_objects(records)

        db.session.commit()

        flash("Lesson schedule uploaded successfully.", "success")
        return redirect(url_for("lesson_schedule"))

    except Exception as e:
        db.session.rollback()

        flash(str(e), "danger")
        return redirect(url_for("lesson_schedule"))


@app.route("/upload-syllabus", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_syllabus():
    try:
        class_name = request.form["class_name"].strip()
        file = request.files.get("pdf_file")

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        file.save(f"static/img/syllabus/{class_name}.pdf")

        flash("Lesson syllabus uploaded successfully.", "success")
        return redirect(url_for("lesson_syllabus"))

    except Exception as e:
        db.session.rollback()

        flash(str(e), "danger")
        return redirect(url_for("lesson_syllabus"))


@app.route("/api/search-curriculum", methods=["POST"])
@login_required
def search_curriculum():
    data = request.json
    class_name = data["class"]
    lesson_schedule_date = data["date"]
    year, month, day = lesson_schedule_date.split("-")
    date_obj = date(day=int(day), month=int(month), year=int(year))

    result = db.session.query(Curriculum).filter_by(class_name=class_name, date=date_obj)

    rows = result.all()

    results = []

    for r in rows:
        results.append({
            "id": r.id,
            "class": r.class_name,
            "subject": r.subject_name,
            "date": r.date,
            "topic": r.topic,
        })

    return {"data": results}


@app.route("/api/upload-videos", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_videos():
    try:
        class_name = request.form["class_name"]
        file = request.files["excel_file"]

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        required_columns = {"ID", "Link"}
        if not required_columns.issubset(df.columns):
            raise ValueError("Missing required columns")

        db.session.query(Video).filter_by(
            class_name=class_name,
        ).delete()

        for index, row in df.iterrows():
            video_id = str(row["ID"])
            video_link = row["Link"]
            video_obj = Video(id=video_id, class_name=class_name, link=video_link)
            db.session.add(video_obj)

        db.session.commit()

        flash("Video Links uploaded successfully", "success")
        return redirect(url_for("tutorial_management"))
    except Exception as e:

        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("tutorial_management"))


@app.route("/api/search-video-links", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def search_video_links():
    data = request.json
    class_ = data["class"]

    videos = db.session.query(Video).filter_by(class_name=class_).all()

    results = []

    for r in videos:
        results.append({
            "id": r.id,
            "link": r.link,
        })

    return {"data": results}


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
    if not school_id or not username or not password or not role:
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
    class_ = filters.get("studentClass")
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

    if class_:
        users = filter(lambda user: str(user.school_id).startswith(class_), users)

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


@app.route('/upload-attendance', methods=['POST'])
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
def upload_attendance():
    try:
        branch = request.form["branch_name"].strip()
        class_ = request.form["class_name"].strip()
        month = request.form["month_name"].strip()

        file = request.files.get('excel_file')

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        # Delete previous record before adding
        db.session.query(AttendanceRecord).filter_by(
            branch=branch,
            class_name=class_,
            month=month
        ).delete()

        for _, row in df.iterrows():
            record = AttendanceRecord(
                branch=branch,
                class_name=class_,
                month=month,
                student_id=int(row["ID"]),
                student_name=helpers.convert_bangla_text(str(row["Student Name"])),

            )
            for i in range(31):
                record.__setattr__(f"d{i + 1}", row[i + 1])

            db.session.add(record)

        db.session.commit()
        flash("Attendance uploaded successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")

    return redirect(url_for("attendance"))


@app.route("/api/search-attendance", methods=["POST"])
def search_attendance():
    data = request.json

    branch_name = data.get("branch")
    class_name = data.get("class")
    month = data.get("month")
    student_id = data.get("student_id")

    if student_id:
        result = db.session.query(AttendanceRecord).filter_by(branch=branch_name, class_name=class_name, month=month,
                                                              student_id=student_id)
    else:
        result = db.session.query(AttendanceRecord).filter_by(branch=branch_name, class_name=class_name, month=month)

    rows = result.all()

    results = []

    for r in rows:
        record = {
            "ID": r.student_id,
            "student_name": r.student_name,
        }
        for i in range(31):
            record[f"d{i + 1}"] = r.__getattribute__(f"d{i + 1}")
        results.append(record)

    return {"data": results}


@app.route('/upload-accounts', methods=['POST'])
def upload_accounts():
    try:
        branch = request.form["branch_name"]
        class_ = request.form["class_name"]
        file = request.files['excel_file']

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        db.session.query(AccountsRecord).filter_by(
            branch=branch,
            class_name=class_,
        ).delete()

        for _, row in df.iterrows():
            record = AccountsRecord(
                branch=branch,
                class_name=class_,
                student_id=int(row["ID"]),
                student_name=helpers.convert_bangla_text(str(row["Student Name"])),
                january=row["January"],
                february=row["February"],
                march=row["March"],
                april=row["April"],
                may=row["May"],
                june=row["June"],
                july=row["July"],
                august=row["August"],
                september=row["September"],
                october=row["October"],
                november=row["November"],
                december=row["December"],
                due=row["Due"]

            )
            db.session.add(record)
        db.session.commit()
        flash("Accounts uploaded successfully.", "success")
        return redirect(url_for("accounts"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("accounts"))


@app.route('/api/search-accounts', methods=['POST'])
def search_accounts():
    data = request.get_json()

    branch = data.get("branch")
    class_ = data.get("class")
    student_id = data.get("student_id")

    query = db.session.query(AccountsRecord).filter_by(
        branch=branch,
        class_name=class_
    )

    if student_id:
        query = query.filter_by(student_id=student_id)

    accounts_records = query.all()

    results = []

    for accounts_record in accounts_records:
        results.append({
            "ID": accounts_record.student_id,
            "student_name": accounts_record.student_name,
            "january": helpers.convert_bangla_text(accounts_record.january),
            "february": helpers.convert_bangla_text(accounts_record.february),
            "march": helpers.convert_bangla_text(accounts_record.march),
            "april": helpers.convert_bangla_text(accounts_record.april),
            "may": helpers.convert_bangla_text(accounts_record.may),
            "june": helpers.convert_bangla_text(accounts_record.june),
            "july": helpers.convert_bangla_text(accounts_record.july),
            "august": helpers.convert_bangla_text(accounts_record.august),
            "september": helpers.convert_bangla_text(accounts_record.september),
            "october": helpers.convert_bangla_text(accounts_record.october),
            "november": helpers.convert_bangla_text(accounts_record.november),
            "december": helpers.convert_bangla_text(accounts_record.december),
            "due": helpers.convert_bangla_text(accounts_record.due),
        })

    return jsonify({
        "success": True,
        "data": results
    })


@app.route('/api/upload-semester-result', methods=['POST'])
def upload_semester_result():
    try:
        file = request.files['excel_file']
        branch = request.form["branch_name"]
        class_ = request.form["class_name"]
        exam = request.form["exam_name"]

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        db.session.query(SemesterResultRecord).filter_by(
            branch=branch,
            class_name=class_,
            exam_name=exam,
        ).delete()

        for _, row in df.iterrows():
            if class_ in ("Play", "Nursery", "One", "Two"):
                new_record = SemesterResultRecord(
                    branch=branch,
                    class_name=class_,
                    exam_name=exam,
                    student_id=int(row["ID"]),
                    student_name=helpers.convert_bangla_text(str(row["Student Name"])),
                    merit=int(row["Merit"]),
                    arabic=round(float(row["Arabic"]), 2),
                    quran=round(float(row["Quran"]), 2),
                    bengali=round(float(row["Bengali"]), 2),
                    english=round(float(row["English"]), 2),
                    math=round(float(row["Math"]), 2),
                    class_test=round(float(row["Class Assessment"]), 2),
                    presence=round(float(row["Attendance"]), 2),
                    total=round(float(row["Total"]), 2),
                    letter_grade=str(row["Letter Grade"])
                )
            else:
                new_record = SemesterResultRecord(
                    branch=branch,
                    class_name=class_,
                    exam_name=exam,
                    student_id=int(row["ID"]),
                    student_name=helpers.convert_bangla_text(str(row["Student Name"])),
                    merit=int(row["Merit"]),
                    arabic=round(float(row["Arabic"]), 2),
                    quran=round(float(row["Quran"]), 2),
                    bengali=round(float(row["Bengali"]), 2),
                    english=round(float(row["English"]), 2),
                    math=round(float(row["Math"]), 2),
                    science=round(float(row["Science"]), 2),
                    bgs=round(float(row["BGS"]), 2),
                    aqaid_and_fiqh=round(float(row["Aqaid & Fiqh"]), 2),
                    class_test=round(float(row["Class Assessment"]), 2),
                    presence=round(float(row["Attendance"]), 2),
                    total=round(float(row["Total"]), 2),
                    letter_grade=str(row["Letter Grade"])
                )
            db.session.add(new_record)

        db.session.commit()
        flash("Semester Assessment Result uploaded successfully.", "success")
        return redirect(url_for("semester_assessment"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("semester_assessment"))


@app.route('/api/search-semester-result', methods=['POST'])
def search_semester_result():
    data = request.json
    branch = data.get("branch")
    class_ = data.get("class")
    exam = data.get("exam")
    student_id = data.get("student_id")

    if student_id:
        records = db.session.query(SemesterResultRecord).filter_by(branch=branch, class_name=class_,
                                                                   exam_name=exam, student_id=student_id).all()
    else:
        records = db.session.query(SemesterResultRecord).filter_by(branch=branch, class_name=class_,
                                                                   exam_name=exam).all()

    results = []
    for record in records:
        new_record = {
            "ID": record.student_id,
            "student_name": record.student_name,
            "merit": helpers.convert_bangla_text(record.merit),
            "arabic": helpers.convert_bangla_text(record.arabic),
            "quran": helpers.convert_bangla_text(record.quran),
            "aqaid_and_fiqh": helpers.convert_bangla_text(record.aqaid_and_fiqh),
            "bengali": helpers.convert_bangla_text(record.bengali),
            "english": helpers.convert_bangla_text(record.english),
            "math": helpers.convert_bangla_text(record.math),
            "science": helpers.convert_bangla_text(record.science),
            "bgs": helpers.convert_bangla_text(record.bgs),
            "class_test": helpers.convert_bangla_text(record.class_test),
            "presence": helpers.convert_bangla_text(record.presence),
            "total": helpers.convert_bangla_text(record.total),
            "letter_grade": record.letter_grade,
        }
        results.append(new_record)

    return {"data": results}


@app.route('/api/upload-class-result', methods=['POST'])
def upload_class_result():
    try:
        branch = request.form["branch_name"]
        class_ = request.form["class_name"]
        month = request.form["month_name"]
        file = request.files['excel_file']

        if not file or file.filename == "":
            raise ValueError("No file uploaded")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Invalid file type")

        df = pd.read_excel(file)

        db.session.query(ClassTestResultRecord).filter_by(
            branch=branch,
            class_name=class_,
            month=month,
        ).delete()

        for _, row in df.iterrows():
            if class_ in ("Play", "Nursery", "One", "Two"):
                new_record = ClassTestResultRecord(
                    branch=branch,
                    class_name=class_,
                    month=month,
                    student_id=int(row["ID"]),
                    student_name=helpers.convert_bangla_text(str(row["Student Name"])),
                    arabic=round(float(row["Arabic"]), 2),
                    bengali=round(float(row["Bengali"]), 2),
                    english=round(float(row["English"]), 2),
                    math=round(float(row["Math"]), 2),
                    total=round(float(row["Total"]), 2),
                )
            else:
                new_record = ClassTestResultRecord(
                    branch=branch,
                    class_name=class_,
                    month=month,
                    student_id=int(row["ID"]),
                    student_name=helpers.convert_bangla_text(str(row["Student Name"])),
                    arabic=round(float(row["Arabic"]), 2),
                    quran=round(float(row["Quran"]), 2),
                    bengali=round(float(row["Bengali"]), 2),
                    english=round(float(row["English"]), 2),
                    math=round(float(row["Math"]), 2),
                    science=round(float(row["Science"]), 2),
                    aqaid_and_fiqh=round(float(row["Aqaid & Fiqh"]), 2),
                    bgs=round(float(row["BGS"]), 2),
                    total=round(float(row["Total"]), 2),
                )

            db.session.add(new_record)

        db.session.commit()

        flash("Class Test Result uploaded successfully.", "success")
        return redirect(url_for("class_assessment"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("class_assessment"))


@app.route('/api/search-class-result', methods=['POST'])
def search_class_result():
    data = request.json
    branch = data.get("branch")
    class_ = data.get("class")
    month = data.get("month")
    student_id = data.get("student_id")

    if student_id:
        records = db.session.query(ClassTestResultRecord).filter_by(branch=branch, class_name=class_, month=month,
                                                                    student_id=student_id).all()
    else:
        records = db.session.query(ClassTestResultRecord).filter_by(branch=branch, class_name=class_, month=month).all()

    results = []
    for record in records:
        new_record = {
            "ID": record.student_id,
            "student_name": record.student_name,
            "arabic": helpers.convert_bangla_text(record.arabic),
            "quran": helpers.convert_bangla_text(record.quran),
            "aqaid_and_fiqh": helpers.convert_bangla_text(record.aqaid_and_fiqh),
            "bengali": helpers.convert_bangla_text(record.bengali),
            "english": helpers.convert_bangla_text(record.english),
            "math": helpers.convert_bangla_text(record.math),
            "science": helpers.convert_bangla_text(record.science),
            "bgs": helpers.convert_bangla_text(record.bgs),
            "total": helpers.convert_bangla_text(record.total),
        }
        results.append(new_record)

    return {"data": results}


@app.route('/api/upload-notice', methods=['POST'])
def upload_notice():
    try:
        img = request.files["img"]
        branch = request.form["branch_name"]
        img.save(f"static/img/notices/{branch}/{datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.png")
        flash("Notice uploaded successfully.", "success")
        return redirect(url_for("notice_board_management"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("notice_board_management"))


@app.route("/api/search-log-info", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def search_login_info():
    data = request.json
    selected_date = data["date"]

    log_infos = db.session.query(LogInfo).filter(
        func.date(LogInfo.login_time) == selected_date
    ).order_by(LogInfo.login_time.desc()).all()

    results = []

    for log in log_infos:
        results.append({
            "username": log.username,
            "login_time": log.login_time.strftime("%d-%m-%Y %I:%M %p")
        })

    return jsonify({
        "data": results
    })


@app.route("/api/search-comments", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def search_comments():
    data = request.json
    selected_date = data["date"]

    comments = db.session.query(Comment).filter(
        func.date(Comment.comment_time) == selected_date
    ).order_by(Comment.comment_time.desc()).all()

    results = []

    for comment in comments:
        results.append({
            "id": comment.id,
            "comment": comment.comment,
            "username": comment.username,
            "reply_txt": comment.reply.reply_txt,
            "comment_time": comment.comment_time.strftime("%d-%m-%Y %I: %M %p"),


        })

    return jsonify({
        "data": results
    })


@app.route('/api/upload-phone-number', methods=['POST'])
def upload_phone_number():
    try:
        branch_name = request.form["branch_name"]
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        new_phone_number = PhoneNumber(branch_name=branch_name, name=name, phone_number=phone_number)
        db.session.add(new_phone_number)
        db.session.commit()
        flash("Phone number uploaded successfully.", "success")
        return redirect(url_for("call_services"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("call_services"))


@app.route('/api/upload-comment', methods=['POST'])
def upload_comment():
    try:
        username = request.form["username"]
        comment = request.form["comment"]

        new_comment = Comment(username=username, comment=comment)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment submitted successfully.", "success")
        return redirect(url_for("student_comment"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("student_comment"))


@app.route("/api/reply-comment", methods=["POST"])
@login_required
@roles_required(ADMIN_ROLE)
def reply_comment():
    try:
        comment_id = int(request.form["comment_db_id"])
        comment_reply = request.form["comment_reply"]


        comment_reply = CommentReply(replier=current_user.username, comment_id=comment_id, reply_txt=comment_reply)
        db.session.add(comment_reply)
        db.session.commit()
        flash("Reply sent successfully.", "success")
        return redirect(url_for("submitted_comments"))
    except Exception as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("submitted_comments"))


# Others ---------------------------------------------------------------------------------------------------------------
@app.route("/video/<int:video_id>")
@login_required
def show_video(video_id):
    if current_user.role == STUDENT_ROLE:
        if str(current_user.school_id)[:1] != str(video_id)[:1]:
            abort(403)

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
