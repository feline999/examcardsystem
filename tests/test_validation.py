import os
import tempfile
from app import create_app
from extensions import db
from models import Student, Fee, UnitRegistration, Attendance, User
from validation import can_generate_exam_card, check_fee_cleared, check_attendance_threshold, check_unit_registration


def setup_app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


def test_validation_rules():
    app = setup_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # create user and student
        u = User(username='s1')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
        student = Student(student_number='S100', name='Stu One', user_id=u.id)
        db.session.add(student)
        db.session.commit()

        # Initially no fees => cleared
        assert check_fee_cleared(student.id)

        # Add unpaid fee
        f = Fee(student_id=student.id, amount_due=100.0, paid=False)
        db.session.add(f)
        db.session.commit()
        assert not check_fee_cleared(student.id)

        # Register units and attendance
        r = UnitRegistration(student_id=student.id, unit_code='MATH101', registered=True)
        db.session.add(r)
        a = Attendance(student_id=student.id, unit_code='MATH101', percent=80.0)
        db.session.add(a)
        db.session.commit()

        # Validate unit registration
        assert check_unit_registration(student.id, ['MATH101'])
        # Attendance threshold
        assert check_attendance_threshold(student.id, 'MATH101', threshold=75.0)

        ok, msg = can_generate_exam_card(student.id, ['MATH101'])
        assert not ok  # because fee unpaid

        # mark fee paid
        f.paid = True
        db.session.commit()
        ok, msg = can_generate_exam_card(student.id, ['MATH101'])
        assert ok
