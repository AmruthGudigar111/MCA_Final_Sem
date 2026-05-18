from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'sastra_mca_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/student_performance_db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Student', 'Faculty', 'Admin', 'Parent'), nullable=False)
    linked_student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=True)
    linked_student = db.relationship('Student', foreign_keys=[linked_student_id], backref='linked_accounts')
    security_question = db.Column(db.String(255), nullable=True)
    security_answer = db.Column(db.String(255), nullable=True)

# Student Model
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(20), nullable=False)
    combination = db.Column(db.Enum('PCMB', 'PCMC'), nullable=False, default='PCMB')

# Academic Record Model with subject theory/practical marks
class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    record_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    attendance_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    academic_year = db.Column(db.Integer, default=2026)
    combination = db.Column(db.Enum('PCMB', 'PCMC'), nullable=True)
    exam_type = db.Column(db.Enum('JUT', 'JFT', 'Mid Term', 'Unit Test', 'Final Exam'), nullable=False, default='Final Exam')
    test_name = db.Column(db.String(100), nullable=True)  # For unit tests
    test_number = db.Column(db.Integer, nullable=True)  # For unit tests
    subject = db.Column(db.String(50), nullable=True)  # For unit tests (specific subject)
    english_theory = db.Column(db.Integer, nullable=True)
    language_subject = db.Column(db.Enum('Kannada', 'Hindi', 'Sanskrit'), nullable=True)
    language_theory = db.Column(db.Integer, nullable=True)
    physics_theory = db.Column(db.Integer, nullable=True)
    physics_practical = db.Column(db.Integer, nullable=True)
    chemistry_theory = db.Column(db.Integer, nullable=True)
    chemistry_practical = db.Column(db.Integer, nullable=True)
    maths_theory = db.Column(db.Integer, nullable=True)
    biology_theory = db.Column(db.Integer, nullable=True)
    biology_practical = db.Column(db.Integer, nullable=True)
    computer_science_theory = db.Column(db.Integer, nullable=True)
    computer_science_practical = db.Column(db.Integer, nullable=True)
    behavior_score = db.Column(db.Integer, default=0)

if __name__ == '__main__':
    with app.app_context():
        try:
            with db.engine.begin() as conn:
                conn.execute(text('DROP TABLE IF EXISTS prediction_results'))
        except Exception as e:
            print(f"Warning dropping prediction_results: {e}")

        db.drop_all()
        db.create_all()

        admin_user = User(
            username='admin',
            full_name='Administrator',
            password_hash=generate_password_hash('admin@123'),
            role='Admin'
        )
        db.session.add(admin_user)
        db.session.commit()

        print("Database recreated successfully with new schema!")
        print("Default admin created: username=admin, password=admin@123")