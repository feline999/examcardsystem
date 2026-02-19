from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
from models import User, Student, ExamCard
from extensions import db, login, limiter
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from uuid import uuid4
from pdf_generator import generate_exam_card
from validation import can_generate_exam_card
import os
from forms import LoginForm

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard') if current_user.is_admin else url_for('auth.student_dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard') if user.is_admin else url_for('auth.student_dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/student')
@login_required
def student_dashboard():
    return render_template('dashboard.html')


@auth_bp.route('/student/exam_card')
@login_required
def generate_my_exam_card():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student profile not found')
        return redirect(url_for('auth.student_dashboard'))

    # consider required units as the student's registered units
    required_units = [r.unit_code for r in student.registrations if r.registered]
    ok, msg = can_generate_exam_card(student.id, required_units)
    if not ok:
        flash(msg)
        return redirect(url_for('auth.student_dashboard'))

    outdir = os.path.join(current_app.root_path, 'generated')
    os.makedirs(outdir, exist_ok=True)
    filename = secure_filename(f'exam_card_{student.student_number}_{uuid4().hex}.pdf')
    filepath = os.path.join(outdir, filename)

    generate_exam_card(student.id, filepath)

    ec = ExamCard(student_id=student.id, filename=filepath)
    db.session.add(ec)
    db.session.commit()

    return send_file(filepath, as_attachment=True)
