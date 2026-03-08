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
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)  # Admin, Teacher, Guardian
    is_active: Mapped[bool] = mapped_column(default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
        admin = User(username='al-aqsa-sharif', role=ADMIN_ROLE)
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()


# Routes -------------------------------------------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, is_active=True).first()

        if user and user.check_password(password):
            login_user(user, duration=timedelta(hours=12))
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
    return render_template('guardian_dashboard.html')


# Options --------------------------------------------------------------------------------------------------------------
@app.route("/lesson-schedule")
@login_required
@roles_required(ADMIN_ROLE, SERVICE_ADMIN_ROLE)
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


@app.route("/call-services")
@login_required
def call_services():
    return render_template("call_services.html")


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


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
    return render_template("admin_user_management.html")


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
    df = pd.read_excel(file)

    for index, row in df.iterrows():
        curriculum_date = str(row["Date"])
        day, month, year = curriculum_date.split("/")
        date_obj = date(day=int(day), month=int(month), year=int(year))
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
    df = pd.read_excel(file)

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
def update_video():
    data = request.json

    video = db.session.get(Video, data["video_id"])
    video.link = data["video_link"]

    db.session.commit()

    return jsonify({"success": True})


# Others ---------------------------------------------------------------------------------------------------------------
@app.route("/video/<int:video_id>")
@login_required
def show_video(video_id):
    video = db.get_or_404(Video, video_id)

    return render_template(
        "video.html",
        video_link=video.link
    )


@app.route('/change-password')
@login_required
def change_password():
    return render_template("change_password.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
