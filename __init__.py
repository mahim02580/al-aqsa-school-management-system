import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Date, Time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import role_required
from dotenv import load_dotenv
import csv
import pandas as pd
from datetime import date

load_dotenv()


def redirect_dashboard(role):
    if role == "admin":
        return redirect(url_for('admin_dashboard'))
    elif role == "teacher":
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('guardian_dashboard'))


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")

db = SQLAlchemy(app, model_class=Base)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)  # admin, teacher, guardian
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


with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='al-aqsa-sharif', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, is_active=True).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect_dashboard(user.role)

        flash('Invalid username or password', 'danger')
        return redirect(url_for("login"))

    return render_template('login.html')


@app.route('/admin-dashboard')
@login_required
@role_required("admin")
def admin_dashboard():
    if current_user.role != 'admin':
        return "Forbidden", 403
    return render_template('admin/admin_dashboard.html')


@app.route("/lesson-schedule")
@login_required
@role_required("admin")
def lesson_schedule():
    return render_template("admin/lesson_schedule.html")


@app.route("/upload_curriculum", methods=["POST"])
@login_required
@role_required("admin")
def upload_curriculum():
    class_name = request.form["class_name"]
    class_obj = db.session.execute(db.select(Class).where(Class.name == class_name)).scalar()
    subject = request.form["subject"]
    subject_obj = db.session.execute(db.select(Subject).where(Subject.name == subject)).scalar()
    file = request.files["excel_file"]

    # read excel
    df = pd.read_csv(file)

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
def update_curriculum():
    data = request.json

    lesson_schedule = db.session.get(Curriculum, int(data["id"]))
    lesson_schedule.topic = data["topic"]
    db.session.commit()

    return {"status": "success"}


@app.route("/attendance")
def attendance():
    return render_template("attendance.html")


@app.route("/accounts")
def accounts():
    return render_template("accounts.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/call-services")
def call_services():
    return render_template("call_services.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/qr-scanner")
def qr_scanner():
    return render_template("qr_scanner.html")


@app.route("/video/<int:video_id>")
def show_video(video_id):
    video = db.session.execute(db.select(Video).where(Video.id == video_id)).scalar()

    if not video:
        return abort(404)

    return render_template(
        "video.html",
        video_link=video.link
    )


@app.route("/admin-user-management")
def admin_user_management():
    return render_template("qr_scanner.html")


@app.route('/teacher-dashboard')
@login_required
@role_required("teacher")
def teacher_dashboard():
    if current_user.role != 'teacher':
        return "Forbidden", 403
    return render_template('teacher_dashboard.html')


@app.route('/guardian-dashboard')
@login_required
@role_required("guardian")
def guardian_dashboard():
    if current_user.role != 'guardian':
        return "Forbidden", 403
    return render_template('student_dashboard.html')


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
