from models import Student, FeePayment, StudentUnit, Attendance, Unit
from sqlalchemy import and_

def can_generate_exam_card(student_id, required_units):
    """
    Check if student is eligible for exam card
    Returns: (bool, message)
    """
    student = Student.query.get(student_id)
    if not student:
        return False, "Student not found"
    
    # Check fee payment (full KES 20,000)
    fee = FeePayment.query.filter_by(
        student_id=student_id,
        semester=student.semester
    ).first()
    
    if not fee or fee.amount_paid < 20000:
        return False, "Fee payment not complete. Required: KES 20,000"
    
    # Check unit registration (all 8 units)
    registered_units = StudentUnit.query.filter_by(
        student_id=student_id,
        semester=student.semester,
        registered=True
    ).count()
    
    if registered_units < 8:
        return False, f"Not enough units registered. Required: 8, Registered: {registered_units}"
    
    # Check attendance (minimum 70%)
    attendance_records = Attendance.query.filter_by(
        student_id=student_id,
        semester=student.semester
    ).all()
    
    for att in attendance_records:
        if att.total_classes > 0:
            percentage = (att.attended_classes / att.total_classes) * 100
            if percentage < 70:
                unit = Unit.query.get(att.unit_id)
                unit_name = unit.name if unit else "Unknown"
                return False, f"Attendance too low for {unit_name}: {percentage:.1f}%"
    
    return True, "Eligible for exam card"


def check_fees_status(student_id, semester):
    """Check if student has paid full fees (20,000)"""
    fee = FeePayment.query.filter_by(
        student_id=student_id,
        semester=semester
    ).first()
    
    if fee and fee.amount_paid >= 20000:
        return True, 20000, fee.amount_paid, 20000 - fee.amount_paid
    elif fee:
        return False, 20000, fee.amount_paid, 20000 - fee.amount_paid
    return False, 20000, 0, 20000


def check_units_registration(student_id, semester):
    """Check if student registered for all 8 units"""
    required_units = Unit.query.filter_by(
        semester=semester,
        is_active=True
    ).count()
    
    registered = StudentUnit.query.filter_by(
        student_id=student_id,
        semester=semester,
        registered=True
    ).count()
    
    units = Unit.query.filter_by(semester=semester, is_active=True).all()
    unit_status = []
    for unit in units:
        status = StudentUnit.query.filter_by(
            student_id=student_id,
            unit_id=unit.id,
            semester=semester
        ).first()
        unit_status.append({
            'code': unit.code,
            'name': unit.name,
            'short_name': unit.short_name,
            'registered': status.registered if status else False
        })
    
    return registered >= required_units, registered, required_units, unit_status


def check_attendance_threshold(student_id, semester, threshold=70):
    """Check attendance with custom threshold"""
    attendance_records = Attendance.query.filter_by(
        student_id=student_id,
        semester=semester
    ).all()
    
    if not attendance_records:
        return False, 0, threshold, "No attendance records"
    
    total_percentage = 0
    for att in attendance_records:
        if att.total_classes > 0:
            percentage = (att.attended_classes / att.total_classes) * 100
            total_percentage += percentage
    
    avg_percentage = total_percentage / len(attendance_records) if attendance_records else 0
    return avg_percentage >= threshold, avg_percentage, threshold