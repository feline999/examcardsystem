from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from models import Student

def generate_exam_card(student_id, filename):
    student = Student.query.get(student_id)
    if not student:
        raise ValueError('Student not found')
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(100, 800, f'Exam Card - {student.name} ({student.student_number})')
    c.drawString(100, 770, 'This is a generated exam card.')
    c.showPage()
    c.save()
    return filename
