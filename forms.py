from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class StudentForm(FlaskForm):
    student_number = StringField('Student Number', validators=[DataRequired(), Length(max=64)])
    name = StringField('Name', validators=[Length(max=128)])
    username = StringField('Username', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create')


class FeeForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    paid = BooleanField('Paid')
    submit = SubmitField('Add Fee')


class RegistrationForm(FlaskForm):
    unit_code = StringField('Unit code', validators=[DataRequired(), Length(max=32)])
    registered = BooleanField('Registered')
    submit = SubmitField('Add Registration')


class AttendanceForm(FlaskForm):
    unit_code = StringField('Unit code', validators=[DataRequired(), Length(max=32)])
    percent = FloatField('Percent', validators=[DataRequired()])
    submit = SubmitField('Add Attendance')
