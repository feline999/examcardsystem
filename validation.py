from models import Fee, UnitRegistration, Attendance

def check_fee_cleared(student_id):
    fees = Fee.query.filter_by(student_id=student_id).all()
    if not fees:
        return True
    return all(f.paid or (f.amount_due or 0) <= 0 for f in fees)


def check_unit_registration(student_id, required_units):
    regs = UnitRegistration.query.filter_by(student_id=student_id).all()
    registered_units = {r.unit_code for r in regs if r.registered}
    return set(required_units).issubset(registered_units)


def check_attendance_threshold(student_id, unit_code, threshold=75.0):
    att = Attendance.query.filter_by(student_id=student_id, unit_code=unit_code).first()
    if not att:
        return False
    return att.percent >= threshold


def can_generate_exam_card(student_id, required_units, attendance_threshold=75.0):
    if not check_fee_cleared(student_id):
        return False, 'Fees not cleared'
    if not check_unit_registration(student_id, required_units):
        return False, 'Not registered for required units'
    for unit in required_units:
        if not check_attendance_threshold(student_id, unit, attendance_threshold):
            return False, f'Attendance below threshold for {unit}'
    return True, 'Eligible'
