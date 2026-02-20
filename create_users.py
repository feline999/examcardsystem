from app import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    # Create all database tables
    db.create_all()
    print("✅ Database tables created!")
    
    # Delete any existing users to start fresh
    User.query.delete()
    
    # Create admin user
    admin = User(username='admin', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create student user
    student = User(username='student', is_admin=False)
    student.set_password('student123')
    db.session.add(student)
    
    db.session.commit()
    print("✅ Admin and student users created!")
    
    # Verify
    print("\n📋 Verification:")
    admin_check = User.query.filter_by(username='admin').first()
    print(f"  Admin exists: {admin_check is not None}")
    if admin_check:
        print(f"  Admin password check: {admin_check.check_password('admin123')}")
    
    student_check = User.query.filter_by(username='student').first()
    print(f"  Student exists: {student_check is not None}")
    if student_check:
        print(f"  Student password check: {student_check.check_password('student123')}")