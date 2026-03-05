import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import role_required
from dotenv import load_dotenv

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
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(username=username, role=role, is_active=True).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect_dashboard(user.role)

        flash('Invalid username, password, or role', 'danger')
        return redirect(url_for("login"))

    return render_template('login.html')

@app.route('/admin-dashboard')
@login_required
@role_required("admin")
def admin_dashboard():
    if current_user.role != 'admin':
        return "Forbidden", 403
    return render_template('admin_dashboard.html')

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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
