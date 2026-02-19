import os
import tempfile
from app import create_app
from extensions import db
from models import Student, User
from pdf_generator import generate_exam_card


def setup_app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


def test_generate_pdf_creates_file():
    app = setup_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = User(username='s2')
        u.set_password('pass')
        db.session.add(u)
        db.session.commit()
        student = Student(student_number='S200', name='Stu Two', user_id=u.id)
        db.session.add(student)
        db.session.commit()

        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        try:
            generate_exam_card(student.id, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            os.remove(path)
