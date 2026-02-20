from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    student_number = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    semester = db.Column(db.String(20))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('student', uselist=False))
    registrations = db.relationship('StudentUnit', backref='student', lazy=True)
    fees = db.relationship('FeePayment', backref='student', lazy=True)
    attendances = db.relationship('Attendance', backref='student', lazy=True)


class StudentUnit(db.Model):
    __tablename__ = 'student_unit'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    registered = db.Column(db.Boolean, default=False)
    semester = db.Column(db.String(20))
    
    # Relationships
    unit = db.relationship('Unit', backref='student_units')


class Unit(db.Model):
    __tablename__ = 'unit'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    short_name = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)


class FeePayment(db.Model):
    __tablename__ = 'fee'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    amount_paid = db.Column(db.Float, default=0)
    semester = db.Column(db.String(20))
    payment_date = db.Column(db.DateTime)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    attended_classes = db.Column(db.Integer, default=0)
    total_classes = db.Column(db.Integer, default=0)
    semester = db.Column(db.String(20))


class ExamCard(db.Model):
    __tablename__ = 'exam_card'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    filename = db.Column(db.String(200))
    generated_date = db.Column(db.DateTime)