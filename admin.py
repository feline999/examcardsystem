from flask import Blueprint, render_template, send_file, current_app, redirect, url_for, flash, request
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from uuid import uuid4
from pdf_generator import generate_exam_card
from models import Student, ExamCard, User, FeePayment, StudentUnit, Attendance, Unit
from extensions import db
from validation import can_generate_exam_card
from forms import StudentForm, FeeForm, RegistrationForm, AttendanceForm

admin_bp = Blueprint('admin', __name__, template_folder='templates')


@admin_bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin:
        return 'Forbidden', 403
    return render_template('admin_dashboard.html')


@admin_bp.route('/generate/<int:student_id>')
@login_required
def generate_for_student(student_id):
    if not current_user.is_admin:
        return 'Forbidden', 403
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found')
        return redirect(url_for('admin.dashboard'))

    # use student's registered units for validation
    required_units = [r.unit_code for r in student.registrations if r.registered]
    ok, msg = can_generate_exam_card(student.id, required_units)
    if not ok:
        flash(msg)
        return redirect(url_for('admin.dashboard'))

    outdir = os.path.join(current_app.root_path, 'generated')
    os.makedirs(outdir, exist_ok=True)
    filename = secure_filename(f'exam_card_{student.student_number}_{uuid4().hex}.pdf')
    filepath = os.path.join(outdir, filename)

    generate_exam_card(student.id, filepath)

    ec = ExamCard(student_id=student.id, filename=filepath)
    db.session.add(ec)
    db.session.commit()

    return send_file(filepath, as_attachment=True)

@admin_bp.route('/students')
@login_required
def students():
    if not current_user.is_admin:
        return 'Forbidden', 403
    all_students = Student.query.all()
    return render_template('admin_students.html', students=all_students)

@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if not current_user.is_admin:
        return 'Forbidden', 403
    form = StudentForm()
    if form.validate_on_submit():
        student_number = form.student_number.data
        name = form.name.data
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('Username exists')
            return redirect(url_for('admin.add_student'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        student = Student(student_number=student_number, name=name, user_id=user.id)
        db.session.add(student)
        db.session.commit()
        flash('Student created')
        return redirect(url_for('admin.students'))
    return render_template('student_form.html', form=form)

@admin_bp.route('/students/<int:student_id>')
@login_required
def student_detail(student_id):
    if not current_user.is_admin:
        return 'Forbidden', 403
    student = Student.query.get_or_404(student_id)
    fee_form = FeeForm()
    reg_form = RegistrationForm()
    att_form = AttendanceForm()
    return render_template('student_detail.html', student=student, fee_form=fee_form, reg_form=reg_form, att_form=att_form)

@admin_bp.route('/students/<int:student_id>/add_fee', methods=['POST'])
@login_required
def add_fee(student_id):
    if not current_user.is_admin:
        return 'Forbidden', 403
    form = FeeForm()
    if form.validate_on_submit():
        amount = float(form.amount.data)
        paid = bool(form.paid.data)
        fee = Fee(student_id=student_id, amount_due=amount, paid=paid)
        db.session.add(fee)
        db.session.commit()
        flash('Fee added')
    else:
        flash('Invalid fee data')
    return redirect(url_for('admin.student_detail', student_id=student_id))

@admin_bp.route('/students/<int:student_id>/add_registration', methods=['POST'])
@login_required
def add_registration(student_id):
    if not current_user.is_admin:
        return 'Forbidden', 403
    form = RegistrationForm()
    if form.validate_on_submit():
        unit_code = form.unit_code.data
        registered = bool(form.registered.data)
        reg = UnitRegistration(student_id=student_id, unit_code=unit_code, registered=registered)
        db.session.add(reg)
        db.session.commit()
        flash('Registration added')
    else:
        flash('Invalid registration data')
    return redirect(url_for('admin.student_detail', student_id=student_id))

@admin_bp.route('/students/<int:student_id>/add_attendance', methods=['POST'])
@login_required
def add_attendance(student_id):
    if not current_user.is_admin:
        return 'Forbidden', 403
    form = AttendanceForm()
    if form.validate_on_submit():
        unit_code = form.unit_code.data
        percent = float(form.percent.data)
        att = Attendance(student_id=student_id, unit_code=unit_code, percent=percent)
        db.session.add(att)
        db.session.commit()
        flash('Attendance added')
    else:
        flash('Invalid attendance data')
    return redirect(url_for('admin.student_detail', student_id=student_id))
