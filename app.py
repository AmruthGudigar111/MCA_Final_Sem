from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pymysql
import cryptography
from predict import StudentPerformancePredictor
import pandas as pd
import os
import uuid
from io import BytesIO
from datetime import datetime
import csv


app = Flask(__name__)
app.secret_key = 'sastra_mca_secret' # Required for session management

# File Upload Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/student_performance_db'
db = SQLAlchemy(app)

# Ensure required user security fields exist on startup
with app.app_context():
    try:
        for column_name, alter_sql in [
            ('security_question', "ALTER TABLE users ADD COLUMN security_question VARCHAR(255) NULL"),
            ('security_answer', "ALTER TABLE users ADD COLUMN security_answer VARCHAR(255) NULL")
        ]:
            exists = db.session.execute(
                text("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema = DATABASE() AND table_name = 'users' AND column_name = :column"),
                {'column': column_name}
            ).scalar()
            if exists == 0:
                db.session.execute(text(alter_sql))
        db.session.commit()
    except Exception:
        db.session.rollback()

# Helpers for preview data storage
PREVIEW_PREFIX = 'preview_'

def _preview_file_path(filename):
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)


def save_preview_to_file(data, prefix):
    filename = f"{prefix}_{uuid.uuid4().hex}.json"
    filepath = _preview_file_path(filename)
    pd.DataFrame(data).to_json(filepath, orient='records')
    return filename


def load_preview_from_file(filename):
    filepath = _preview_file_path(filename)
    if not os.path.exists(filepath):
        return None
    df = pd.read_json(filepath, orient='records')
    return df.to_dict('records')


def remove_preview_file(filename):
    filepath = _preview_file_path(filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass

# Initialize AI Predictor
predictor = StudentPerformancePredictor()
predictor.load_model()  # Try to load existing model

# User Model with Name Attribute and Roles
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

# Student model with science combination selection
class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reg_number = db.Column(db.String(20), nullable=False)
    combination = db.Column(db.Enum('PCMB', 'PCMC'), nullable=False, default='PCMB')

# Academic record with subject theory/practical fields
class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    record_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    attendance_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    academic_year = db.Column(db.Integer, default=2026)
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

    def _subject_total(self, theory, practical=None):
        if theory is None:
            return None
        return theory + (practical or 0)

    @property
    def subject_totals(self):
        totals = {}
        
        # Always include English
        if self.english_theory is not None:
            totals['English'] = self._subject_total(self.english_theory)
        
        # Include language only for Final Exam
        if self.exam_type == 'Final Exam' and self.language_theory is not None:
            totals[self.language_subject or 'Language'] = self._subject_total(self.language_theory)
        
        # Physics, Chemistry, Maths for JUT, JFT, Mid Term, Final Exam
        if self.exam_type in ['JUT', 'JFT', 'Mid Term', 'Final Exam']:
            if self.physics_theory is not None:
                totals['Physics'] = self._subject_total(self.physics_theory, self.physics_practical)
            if self.chemistry_theory is not None:
                totals['Chemistry'] = self._subject_total(self.chemistry_theory, self.chemistry_practical)
            if self.maths_theory is not None:
                totals['Maths'] = self._subject_total(self.maths_theory)
        
        # Biology for PCMB in JUT, JFT, Mid Term, Final Exam
        if self.exam_type in ['JUT', 'JFT', 'Mid Term', 'Final Exam'] and self.biology_theory is not None:
            totals['Biology'] = self._subject_total(self.biology_theory, self.biology_practical)
        
        # Computer Science for PCMC in JUT, JFT, Mid Term, Final Exam
        if self.exam_type in ['JUT', 'JFT', 'Mid Term', 'Final Exam'] and self.computer_science_theory is not None:
            totals['Computer Science'] = self._subject_total(self.computer_science_theory, self.computer_science_practical)
        
        # For Unit Tests, only include the specific subject
        if self.exam_type == 'Unit Test' and self.subject:
            if self.subject == 'English' and self.english_theory is not None:
                totals['English'] = self._subject_total(self.english_theory)
            elif self.subject == 'Language' and self.language_theory is not None:
                totals[self.language_subject or 'Language'] = self._subject_total(self.language_theory)
            elif self.subject == 'Physics' and self.physics_theory is not None:
                totals['Physics'] = self._subject_total(self.physics_theory, self.physics_practical)
            elif self.subject == 'Chemistry' and self.chemistry_theory is not None:
                totals['Chemistry'] = self._subject_total(self.chemistry_theory, self.chemistry_practical)
            elif self.subject == 'Maths' and self.maths_theory is not None:
                totals['Maths'] = self._subject_total(self.maths_theory)
            elif self.subject == 'Biology' and self.biology_theory is not None:
                totals['Biology'] = self._subject_total(self.biology_theory, self.biology_practical)
            elif self.subject == 'Computer Science' and self.computer_science_theory is not None:
                totals['Computer Science'] = self._subject_total(self.computer_science_theory, self.computer_science_practical)
        
        return totals

    @property
    def total_marks(self):
        valid_marks = [m for m in self.subject_totals.values() if m is not None]
        return sum(valid_marks) if valid_marks else 0

    @property
    def average_marks(self):
        valid_marks = [m for m in self.subject_totals.values() if m is not None]
        return sum(valid_marks) / len(valid_marks) if valid_marks else 0

    @property
    def overall_performance(self):
        return self.average_marks

    @property
    def percentage(self):
        """Calculate percentage based on total marks out of expected total"""
        subject_count = len(self.subject_totals)
        expected_total = subject_count * 100  # Each subject out of 100
        return (self.total_marks / expected_total * 100) if expected_total > 0 else 0

    @property
    def classification(self):
        """Classify based on percentage"""
        percentage = self.percentage
        if percentage >= 95:
            return 'Distinction'
        elif percentage >= 85:
            return 'First Class'
        elif percentage >= 60:
            return 'Second Class'
        elif percentage >= 50:
            return 'Third Class'
        elif percentage >= 35:
            return 'Pass'
        else:
            return 'Fail'

@app.route('/')
def login_page():
    role = request.args.get('role', '').strip().capitalize()
    return render_template('login.html', selected_role=role)

@app.route('/login', methods=['POST'])
def login():
    # Fix: Ensure password is a string, not None
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # Process 1.0: Authenticate against the Database [cite: 66, 113]
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.user_id
        session['role'] = user.role
        session['name'] = user.full_name
        session['linked_student_id'] = user.linked_student_id
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials. Please try again.')
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user:
        session.clear()
        return redirect(url_for('login_page'))

    return render_template('dashboard.html', role=user.role, name=user.full_name or user.username)

@app.route('/predictions')
def predictions():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    role = session.get('role')
    predictions = []

    if role in ['Faculty', 'Admin']:
        records = AcademicRecord.query.order_by(AcademicRecord.student_id, AcademicRecord.record_id.desc()).all()
        latest_records = {}
        for record in records:
            if record.student_id not in latest_records:
                latest_records[record.student_id] = record

        for student_id, record in latest_records.items():
            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                continue

            avg_marks = record.average_marks or 0
            if predictor.model and predictor.scaler:
                risk, confidence = predictor.predict_risk(float(record.attendance_percentage or 0), float(avg_marks), int(record.behavior_score or 0))
                confidence_text = f"{confidence:.1%}" if confidence is not None else 'N/A'
            else:
                risk, confidence_text = 'Unknown', 'N/A'

            predictions.append({
                'student_id': student.student_id,
                'name': student.name,
                'attendance': float(record.attendance_percentage or 0),
                'marks': round(float(avg_marks), 1),
                'risk': risk,
                'confidence': confidence_text
            })
    else:
        linked_id = session.get('linked_student_id')
        if not linked_id:
            return render_template('error_page.html', title='Performance Not Available', message='No linked student information found for your account.', return_url=url_for('dashboard'))

        record = AcademicRecord.query.filter_by(student_id=linked_id).order_by(AcademicRecord.record_id.desc()).first()
        student = Student.query.filter_by(student_id=linked_id).first()
        if not record or not student:
            return render_template('error_page.html', title='Performance Not Available', message='No prediction data is available for your account yet.', return_url=url_for('dashboard'))

        avg_marks = record.average_marks or 0
        if predictor.model and predictor.scaler:
            risk, confidence = predictor.predict_risk(float(record.attendance_percentage or 0), float(avg_marks), int(record.behavior_score or 0))
            confidence_text = f"{confidence:.1%}" if confidence is not None else 'N/A'
        else:
            risk, confidence_text = 'Unknown', 'N/A'

        predictions.append({
            'student_id': student.student_id,
            'name': student.name,
            'attendance': float(record.attendance_percentage or 0),
            'marks': round(float(avg_marks), 1),
            'risk': risk,
            'confidence': confidence_text
        })

    return render_template('predictions.html', predictions=predictions)

@app.route('/study_plan/<int:student_id>')
def study_plan(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    role = session.get('role')
    
    # Check permissions
    if role not in ['Faculty', 'Admin']:
        linked_id = session.get('linked_student_id')
        if not linked_id or linked_id != student_id:
            return render_template('error_page.html', title='Access Denied', 
                                 message='You can only view your own study plan.', 
                                 return_url=url_for('dashboard'))

    # Get student's latest academic record
    record = AcademicRecord.query.filter_by(student_id=student_id).order_by(AcademicRecord.record_id.desc()).first()
    student = Student.query.filter_by(student_id=student_id).first()
    
    if not record or not student:
        return render_template('error_page.html', title='Data Not Found', 
                             message='No academic data found for this student.', 
                             return_url=url_for('dashboard'))

    # Generate study plan
    student_data = {
        'subject_totals': record.subject_totals,
        'attendance': float(record.attendance_percentage or 0),
        'behavior_score': int(record.behavior_score or 0)
    }
    
    study_plan_data = predictor.generate_study_plan(student_data)
    
    return render_template('study_plan.html', 
                         student=student, 
                         record=record, 
                         study_plan=study_plan_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    student_name = None
    student_id = None
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        security_question = request.form.get('security_question', '')
        security_answer = request.form.get('security_answer', '')

        if not student_id:
            flash('Please enter your student ID.')
            return render_template('register_student.html', student_name=None, student_id=student_id)

        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            flash('Please enter the correct student ID. If this still persists contact the administrator.')
            return render_template('register_student.html', student_name=None, student_id=student_id)

        student_name = student.name

        # If passwords are provided, create the account
        if password and confirm_password:
            if password != confirm_password:
                flash('Passwords do not match.')
                return render_template('register_student.html', student_name=student_name, student_id=student_id)

            if not security_question or not security_answer:
                flash('Please select a security question and provide an answer.')
                return render_template('register_student.html', student_name=student_name, student_id=student_id)

            username = str(student_id)
            if User.query.filter_by(username=username).first():
                flash('An account already exists for this student ID.')
                return render_template('register_student.html', student_name=student_name, student_id=student_id)

            password_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                full_name=student_name,
                password_hash=password_hash,
                role='Student',
                linked_student_id=student.student_id,
                security_question=security_question,
                security_answer=security_answer.lower().strip()
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Student account created successfully. You can login now.')
            return redirect(url_for('login_page'))
        else:
            # Just verifying student ID, show the form for password entry
            return render_template('register_student.html', student_name=student_name, student_id=student_id)

    return render_template('register_student.html', student_name=student_name, student_id=student_id)

@app.route('/register_parent', methods=['GET', 'POST'])
def register_parent():
    student = None
    reg_number = ''
    if request.method == 'POST':
        reg_number = request.form.get('reg_number', '').strip()
        parent_name = request.form.get('parent_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        security_question = request.form.get('security_question', '')
        security_answer = request.form.get('security_answer', '')

        if not reg_number:
            flash('Please enter the student registration number.')
            return render_template('register_parent.html', student=None, reg_number=reg_number)

        student = Student.query.filter_by(reg_number=reg_number).first()
        if not student:
            flash('No student found for the provided registration number.')
            return render_template('register_parent.html', student=None, reg_number=reg_number)

        if password and confirm_password and parent_name:
            if password != confirm_password:
                flash('Passwords do not match.')
                return render_template('register_parent.html', student=student, reg_number=reg_number)

            if not security_question or not security_answer:
                flash('Please select a security question and provide an answer.')
                return render_template('register_parent.html', student=student, reg_number=reg_number)

            username = reg_number
            if User.query.filter_by(username=username).first():
                flash('An account already exists for this registration number.')
                return render_template('register_parent.html', student=student, reg_number=reg_number)

            password_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                full_name=parent_name,
                password_hash=password_hash,
                role='Parent',
                linked_student_id=student.student_id,
                security_question=security_question,
                security_answer=security_answer.lower().strip()
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Parent account created successfully. Use the student registration number as your username to login.')
            return redirect(url_for('login_page'))

        return render_template('register_parent.html', student=student, reg_number=reg_number)

    return render_template('register_parent.html', student=None, reg_number=reg_number)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        student_id = request.form.get('student_id', '').strip()
        reg_number = request.form.get('reg_number', '').strip()

        user = None
        if username:
            user = User.query.filter_by(username=username).first()
        elif student_id:
            # For students, username is student_id
            user = User.query.filter_by(username=student_id, role='Student').first()
        elif reg_number:
            # For parents, username is parent_regnumber
            username_pattern = f"parent_{reg_number}"
            user = User.query.filter_by(username=username_pattern, role='Parent').first()

        if not user:
            flash('User not found. Please check your details.')
            return render_template('forgot_password.html')

        # Store user_id in session for security question verification
        session['reset_user_id'] = user.user_id
        return redirect(url_for('security_question'))

    return render_template('forgot_password.html')

@app.route('/security_question', methods=['GET', 'POST'])
def security_question():
    if 'reset_user_id' not in session:
        return redirect(url_for('forgot_password'))

    user = User.query.filter_by(user_id=session['reset_user_id']).first()
    if not user:
        session.pop('reset_user_id', None)
        return redirect(url_for('forgot_password'))

    if not user.security_question:
        flash('Security question is not set for this account. Contact the administrator.')
        session.pop('reset_user_id', None)
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        answer = request.form.get('answer', '').strip().lower()
        if answer == user.security_answer:
            session['verified_user_id'] = user.user_id
            session.pop('reset_user_id', None)
            return redirect(url_for('reset_password'))
        else:
            flash('Incorrect answer to security question.')

    return render_template('security_question.html', question=user.security_question)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'verified_user_id' not in session:
        return redirect(url_for('forgot_password'))

    user = User.query.filter_by(user_id=session['verified_user_id']).first()
    if not user:
        session.pop('verified_user_id', None)
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if password != confirm_password:
            flash('Passwords do not match.')
        elif len(password) < 6:
            flash('Password must be at least 6 characters long.')
        else:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            session.pop('verified_user_id', None)
            flash('Password reset successfully. You can now login with your new password.')
            return redirect(url_for('login_page'))

    return render_template('reset_password.html')

@app.route('/my_performance')
def my_performance():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    linked_id = session.get('linked_student_id')
    if not linked_id:
        flash('No linked student account found. Contact administrator for access.')
        return redirect(url_for('dashboard'))
    return redirect(url_for('subject_performance', student_id=linked_id))

@app.route('/view_student_marks')
def view_student_marks():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    def group_records(records):
        grouped = []
        current = None
        for record, student in records:
            if current is None or current['student'].student_id != student.student_id:
                current = {'student': student, 'records': [record]}
                grouped.append(current)
            else:
                current['records'].append(record)
        return grouped

    role = session.get('role')
    if role in ['Faculty', 'Admin']:
        records = db.session.query(AcademicRecord, Student).join(Student).order_by(Student.student_id, AcademicRecord.record_id).all()
        students = group_records(records)
        return render_template('student_marks.html', students=students, title='All Student Marks')

    linked_id = session.get('linked_student_id')
    if not linked_id:
        return render_template('error_page.html', title='Performance Not Found', message='No linked student account found for your profile. Contact the administrator.', return_url=url_for('dashboard'))

    records = db.session.query(AcademicRecord, Student).join(Student).filter(Student.student_id == linked_id).order_by(AcademicRecord.record_id).all()
    if not records:
        return render_template('error_page.html', title='Performance Not Found', message='No marks or performance records are available for your account yet.', return_url=url_for('dashboard'))

    students = group_records(records)
    return render_template('student_marks.html', students=students, title='My Marks', own_view=True)

@app.route('/search_student')
def search_student():
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash('Unauthorized: Only Faculty or Admins can search students.')
        return redirect(url_for('dashboard'))

    query = request.args.get('query', '').strip()
    students = []

    if query:
        # Search by student ID, name, or registration number
        if query.isdigit():
            students = Student.query.filter(
                or_(
                    Student.student_id == int(query),
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%')
                )
            ).all()
        else:
            students = Student.query.filter(
                or_(
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%')
                )
            ).all()

    return render_template('search_student.html', students=students, query=query)

def admin_only_redirect():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized: Only Admins can access this page.")
        return redirect(url_for('dashboard'))
    return None

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized: Only Faculty or Admins can add students.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        reg_number = request.form.get('reg_number')
        combination = request.form.get('combination', 'PCMB')
        
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            flash("Student with this ID already exists.")
            return render_template('add_student.html')
        
        new_student = Student(
            student_id=student_id,
            name=name,
            reg_number=reg_number,
            combination=combination
        )
        db.session.add(new_student)
        db.session.commit()
        flash("Student added successfully!")
        return redirect(url_for('dashboard'))
    
    return render_template('add_student.html')

@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized: Only Faculty or Admins can input attendance.")
        return redirect(url_for('dashboard'))

    prediction = None
    if request.method == 'POST':
        SID = request.form.get('student_id')
        attendance_pct = request.form.get('attendance_percentage')
        exam_type = request.form.get('exam_type')
        academic_year = request.form.get('academic_year', 2026)
        test_name = request.form.get('test_name')
        test_number = request.form.get('test_number')
        subject = request.form.get('subject')
        behavior_score = request.form.get('behavior_score', 0)

        student = Student.query.filter_by(student_id=SID).first()
        if not student:
            flash("Student not found. Please add the student first.")
            return render_template('attendance_form.html')

        if not exam_type:
            flash("Exam type is required.")
            return render_template('attendance_form.html')

        def parse_int(value):
            return int(value) if value not in [None, ''] else None

        try:
            language_subject = request.form.get('language_subject')
            language_theory = parse_int(request.form.get('language_theory'))
            english_theory = parse_int(request.form.get('english_theory'))

            if english_theory is None:
                flash('English marks are required.')
                return render_template('attendance_form.html')

            if not language_subject or language_subject not in ['Kannada', 'Hindi', 'Sanskrit'] or language_theory is None:
                flash('Please select one language subject and enter its marks.')
                return render_template('attendance_form.html')

            record_data = {
                'student_id': SID,
                'attendance_percentage': attendance_pct,
                'academic_year': int(academic_year),
                'exam_type': exam_type,
                'test_name': test_name if exam_type == 'Unit Test' else None,
                'test_number': parse_int(test_number) if exam_type == 'Unit Test' else None,
                'subject': subject if exam_type == 'Unit Test' else None,
                'english_theory': english_theory,
                'language_subject': language_subject,
                'language_theory': language_theory,
                'physics_theory': parse_int(request.form.get('physics_theory')),
                'physics_practical': parse_int(request.form.get('physics_practical')),
                'chemistry_theory': parse_int(request.form.get('chemistry_theory')),
                'chemistry_practical': parse_int(request.form.get('chemistry_practical')),
                'maths_theory': parse_int(request.form.get('maths_theory')),
                'biology_theory': parse_int(request.form.get('biology_theory')),
                'biology_practical': parse_int(request.form.get('biology_practical')),
                'computer_science_theory': parse_int(request.form.get('computer_science_theory')),
                'computer_science_practical': parse_int(request.form.get('computer_science_practical')),
                'behavior_score': parse_int(behavior_score) or 0
            }
        except ValueError:
            flash("Invalid marks format. Please enter numeric values.")
            return render_template('attendance_form.html')

        new_record = AcademicRecord(**record_data)
        db.session.add(new_record)
        db.session.commit()

        total_marks = new_record.total_marks
        avg_marks = new_record.average_marks
        risk, confidence = predictor.predict_risk(float(attendance_pct), float(avg_marks), int(record_data['behavior_score']))
        if risk:
            prediction = {
                'risk': risk,
                'confidence': f"{confidence:.1%}",
                'student_name': student.name
            }

        flash("Record added successfully!")

    return render_template('attendance_form.html', prediction=prediction)

@app.route('/manage_students')
def manage_students():
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    query = request.args.get('query', '').strip()
    if query:
        if query.isdigit():
            students = Student.query.filter(
                or_(
                    Student.student_id == int(query),
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%'),
                    Student.combination.ilike(f'%{query}%')
                )
            ).order_by(Student.student_id).all()
        else:
            students = Student.query.filter(
                or_(
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%'),
                    Student.combination.ilike(f'%{query}%')
                )
            ).order_by(Student.student_id).all()
    else:
        students = Student.query.order_by(Student.student_id).all()

    return render_template('manage_students.html', students=students, query=query)

@app.route('/export_students')
def export_students():
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))

    query = request.args.get('query', '').strip()
    students_query = Student.query
    if query:
        if query.isdigit():
            students_query = students_query.filter(
                or_(
                    Student.student_id == int(query),
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%'),
                    Student.combination.ilike(f'%{query}%')
                )
            )
        else:
            students_query = students_query.filter(
                or_(
                    Student.name.ilike(f'%{query}%'),
                    Student.reg_number.ilike(f'%{query}%'),
                    Student.combination.ilike(f'%{query}%')
                )
            )

    students = students_query.order_by(Student.student_id).all()
    data = [
        {
            'student_id': student.student_id,
            'name': student.name,
            'reg_number': student.reg_number,
            'combination': student.combination
        }
        for student in students
    ]

    if not data:
        flash('No students found to export.')
        return redirect(url_for('manage_students'))

    output = BytesIO()
    df = pd.DataFrame(data)
    df.to_excel(output, index=False, sheet_name='Students')
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name='students_export.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        flash('Student not found.')
        return redirect(url_for('manage_students'))

    if request.method == 'POST':
        student.name = request.form.get('name')
        student.reg_number = request.form.get('reg_number')
        student.combination = request.form.get('combination', student.combination)
        db.session.commit()
        flash('Student information updated successfully.')
        return redirect(url_for('manage_students'))

    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        AcademicRecord.query.filter_by(student_id=student_id).delete()
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully.')
    else:
        flash('Student not found.')
    return redirect(url_for('manage_students'))

@app.route('/bulk_delete_students', methods=['POST'])
def bulk_delete_students():
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    student_ids = request.form.getlist('student_ids')
    if not student_ids:
        flash('No students selected for deletion.')
        return redirect(url_for('manage_students'))

    deleted_count = 0
    for student_id in student_ids:
        student = Student.query.filter_by(student_id=int(student_id)).first()
        if student:
            AcademicRecord.query.filter_by(student_id=int(student_id)).delete()
            db.session.delete(student)
            deleted_count += 1

    db.session.commit()
    flash(f'Successfully deleted {deleted_count} student(s).')
    return redirect(url_for('manage_students'))

@app.route('/manage_users')
def manage_users():
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    query = request.args.get('query', '').strip()
    if query:
        users = User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.full_name.ilike(f'%{query}%'),
                User.role.ilike(f'%{query}%')
            )
        ).order_by(User.user_id).all()
    else:
        users = User.query.order_by(User.user_id).all()

    return render_template('manage_users.html', users=users, query=query)

@app.route('/export_users')
def export_users():
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))

    query = request.args.get('query', '').strip()
    users_query = User.query
    if query:
        users_query = users_query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.full_name.ilike(f'%{query}%'),
                User.role.ilike(f'%{query}%')
            )
        )

    users = users_query.order_by(User.user_id).all()
    data = [
        {
            'user_id': user.user_id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role
        }
        for user in users
    ]

    if not data:
        flash('No users found to export.')
        return redirect(url_for('manage_users'))

    output = BytesIO()
    df = pd.DataFrame(data)
    df.to_excel(output, index=False, sheet_name='Users')
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name='users_export.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    user = User.query.filter_by(user_id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.')
    else:
        flash('User not found.')
    return redirect(url_for('manage_users'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        role = request.form.get('role')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return render_template('add_user.html')

        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            full_name=full_name,
            password_hash=password_hash,
            role=role
        )

        if role in ['Faculty', 'Student', 'Parent']:
            if not security_question or not security_answer:
                flash('Security question and answer are required for this role.')
                return render_template('add_user.html')
            new_user.security_question = security_question
            new_user.security_answer = security_answer.lower().strip()

        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully.')
        return redirect(url_for('manage_users'))

    return render_template('add_user.html')

@app.route('/change_user_password/<int:user_id>', methods=['GET', 'POST'])
def change_user_password(user_id):
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('manage_users'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or not confirm_password:
            flash('Please fill both password fields.')
        elif password != confirm_password:
            flash('Passwords do not match.')
        else:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            flash('Password updated successfully.')
            return redirect(url_for('manage_users'))

    return render_template('change_user_password.html', user=user)

@app.route('/train_model')
def train_model():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized: Only Admins can train the model.")
        return redirect(url_for('dashboard'))
    
    # Generate sample data and train model
    sample_data = predictor.generate_sample_data()
    accuracy = predictor.train_model(sample_data)
    
    flash(f"Model trained successfully! Accuracy: {accuracy:.2f}")
    return redirect(url_for('dashboard'))

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if session.get('role') not in ['Faculty', 'Admin']:
        flash('Unauthorized: Only Faculty or Admins can view analytics.')
        return redirect(url_for('dashboard'))

    # Get performance analytics data
    records = db.session.query(AcademicRecord, Student).join(Student).all()

    analytics_data = []
    for record, student in records:
        analytics_data.append({
            'student_id': student.student_id,
            'name': student.name,
            'reg_number': student.reg_number,
            'combination': student.combination,
            'attendance': record.attendance_percentage,
            'total_marks': round(record.total_marks, 1),
            'average_marks': round(record.average_marks, 1),
            'percentage': round(record.percentage, 2),
            'classification': record.classification,
            'behavior_score': record.behavior_score,
            'subjects': record.subject_totals
        })

    return render_template('analytics.html', analytics=analytics_data)

@app.route('/download_student_template')
def download_student_template():
    """Download CSV template for bulk student upload"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized")
        return redirect(url_for('dashboard'))

    # Create template DataFrame
    template_data = {
        'student_id': ['260001', '260002', '260003'],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'reg_number': ['S20260001', 'S20260002', 'S20260003'],
        'combination': ['PCMB', 'PCMC', 'PCMB']
    }
    df = pd.DataFrame(template_data)

    # Save to CSV
    filename = f'student_template.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(filepath, index=False)

    # Send file for download
    return send_file(filepath, as_attachment=True, download_name='student_template.csv')

@app.route('/upload_students', methods=['GET', 'POST'])
def upload_students():
    """Bulk upload students from Excel"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized: Only Faculty or Admins can upload students.")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(url_for('dashboard'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('dashboard'))
        
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            flash('Please upload an Excel (.xlsx, .xls) or CSV (.csv) file (.xlsx or .xls)')
            return redirect(request.referrer)
        
        try:
            # Read Excel file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_cols = ['student_id', 'name', 'reg_number']
            if not all(col in df.columns for col in required_cols):
                flash(f'Excel must have columns: {", ".join(required_cols)}')
                return redirect(request.referrer)
            
            preview_data = df.to_dict('records')
            if 'student_preview_file' in session:
                remove_preview_file(session.pop('student_preview_file'))

            preview_file = save_preview_to_file(preview_data, 'students')
            session['student_preview_file'] = preview_file
            session['preview_type'] = 'students'

            return render_template('preview_data.html', data=preview_data, type='students')
        
        except Exception as e:
            flash(f'Error reading file: {str(e)}')
            return redirect(request.referrer)
    
    return render_template('upload_students.html')

@app.route('/confirm_upload_students', methods=['POST'])
def confirm_upload_students():
    """Confirm and save students from preview"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized")
        return redirect(url_for('dashboard'))
    
    if 'student_preview_file' not in session:
        flash("No preview data found")
        return redirect(url_for('upload_students'))
    
    preview_data = load_preview_from_file(session['student_preview_file'])
    if preview_data is None:
        flash("Preview data expired or was removed.")
        session.pop('student_preview_file', None)
        return redirect(url_for('upload_students'))

    success_count = 0
    error_count = 0
    
    for row in preview_data:
        try:
            # Check if student already exists
            existing = Student.query.filter_by(student_id=row['student_id']).first()
            if not existing:
                new_student = Student(
                    student_id=row['student_id'],
                    name=row['name'],
                    reg_number=row['reg_number'],
                    combination=row.get('combination', 'PCMB') or 'PCMB'
                )
                db.session.add(new_student)
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
    
    db.session.commit()
    remove_preview_file(session.pop('student_preview_file', None))
    
    result_summary = {
        'success': success_count,
        'errors': error_count,
        'message': f'Successfully added {success_count} students. {error_count} duplicates skipped.'
    }
    return render_template('preview_data.html', data=preview_data, type='students', result_summary=result_summary, import_complete=True)

@app.route('/download_marks_template')
def download_marks_template():
    """Download CSV template for bulk marks upload"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized")
        return redirect(url_for('dashboard'))

    template_data = {
        'student_id': ['260001', '260002', '260003', '260004', '260005', '260006'],
        'exam_type': ['Final Exam', 'JUT', 'JFT', 'Mid Term', 'Unit Test', 'Unit Test'],
        'test_name': [None, None, None, None, 'Chapter 1 Test', 'Chapter 2 Test'],
        'test_number': [None, None, None, None, 1, 2],
        'subject': [None, None, None, None, 'Physics', 'Chemistry'],
        'attendance_percentage': [85, 90, 88, 92, 85, 87],
        'combination': ['PCMB', 'PCMC', 'PCMC', 'PCMB', 'PCMB', 'PCMC'],
        'academic_year': [2026, 2026, 2026, 2026, 2026, 2026],

        'english_theory': [80, 85, 83, 87, None, None],
        'language_subject': ['Kannada', 'Hindi', 'Sanskrit', 'Hindi', None, None],
        'language_theory': [78, 82, 80, 84, None, None],

        'physics_theory': [65, 70, 68, 70, 25, None],
        'physics_practical': [20, 22, 21, 23, 10, None],

        'chemistry_theory': [60, 68, 69, 70, None, 25],
        'chemistry_practical': [25, 27, 26, 28, None, 10],

        'maths_theory': [70, 88, 85, 90, None, None],

        'biology_theory': [58, None, None, 58, None, None],
        'biology_practical': [28, None, None, 28, None, None],

        'computer_science_theory': [None, 70, 69, None, None, None],
        'computer_science_practical': [None, 30, 29, None, None, None],

        'behavior_score': [8, 9, 8, 8, 8, 8]
    }

    df = pd.DataFrame(template_data)

    # Save to CSV (no formulas will change values)
    filename = f'marks_template.csv'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df.to_csv(filepath, index=False)

    # Send file for download
    return send_file(filepath, as_attachment=True, download_name='marks_template.csv')

@app.route('/upload_marks', methods=['GET', 'POST'])
def upload_marks():
    """Bulk upload marks from Excel"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized: Only Faculty or Admins can upload marks.")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.referrer)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.referrer)
        
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            flash('Please upload an Excel (.xlsx, .xls) or CSV (.csv) file')
            return redirect(request.referrer)
        
        try:
            # Read file based on extension
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            required_cols = [
                'student_id', 'exam_type', 'attendance_percentage', 'combination',
                'academic_year',
                'english_theory',
                'language_subject',
                'language_theory',
                'physics_theory', 'physics_practical',
                'chemistry_theory', 'chemistry_practical',
                'maths_theory',
                'biology_theory', 'biology_practical',
                'computer_science_theory', 'computer_science_practical',
                'behavior_score'
            ]
            
            if not all(col in df.columns for col in required_cols):
                flash(f'Excel must include columns: {", ".join(required_cols)}')
                return redirect(request.referrer)
            
            preview_data = df.to_dict('records')
            if 'marks_preview_file' in session:
                remove_preview_file(session.pop('marks_preview_file'))

            preview_file = save_preview_to_file(preview_data, 'marks')
            session['marks_preview_file'] = preview_file

            return render_template('preview_data.html', data=preview_data, type='marks')
        
        except Exception as e:
            flash(f'Error reading file: {str(e)}')
            return redirect(request.referrer)
    
    return render_template('upload_marks.html')

@app.route('/confirm_upload_marks', methods=['POST'])
def confirm_upload_marks():
    """Confirm and save marks from preview"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized")
        return redirect(url_for('dashboard'))
    
    if 'marks_preview_file' not in session:
        flash("No preview data found")
        return redirect(url_for('upload_marks'))
    
    preview_data = load_preview_from_file(session['marks_preview_file'])
    if preview_data is None:
        flash("Preview data expired or was removed.")
        session.pop('marks_preview_file', None)
        return redirect(url_for('upload_marks'))

    success_count = 0
    error_count = 0
    row_errors = []
    
    def parse_value(value):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        if pd.isna(value):
            return None
        try:
            return int(value)
        except Exception:
            try:
                return int(float(value))
            except Exception:
                return None

    def parse_student_id(value):
        student_id = parse_value(value)
        if student_id is None:
            return None
        return student_id

    for idx, row in enumerate(preview_data, start=1):
        try:
            student_id_val = parse_student_id(row.get('student_id'))
            if student_id_val is None:
                error_count += 1
                row_errors.append({'row': idx, 'reason': 'Missing or invalid student_id', 'row_data': row})
                continue

            student = Student.query.filter_by(student_id=student_id_val).first()
            if not student:
                error_count += 1
                row_errors.append({'row': idx, 'reason': f'Student ID {student_id_val} not found', 'row_data': row})
                continue

            selected_combo = str(row.get('combination', '')).strip().upper()
            if selected_combo != student.combination:
                error_count += 1
                row_errors.append({'row': idx, 'reason': f'Combination mismatch (expected {student.combination})', 'row_data': row})
                continue
            
            attendance_value = row.get('attendance_percentage', 0)
            attendance_pct = float(attendance_value) if attendance_value not in [None, ''] and not pd.isna(attendance_value) else 0
            
            academic_year_val = parse_value(row.get('academic_year', 2026))
            if academic_year_val is None:
                academic_year_val = 2026

            language_subject = str(row.get('language_subject', '')).strip().title() if row.get('language_subject') else None
            language_theory = parse_value(row.get('language_theory'))
            english_theory = parse_value(row.get('english_theory'))

            if english_theory is None:
                error_count += 1
                row_errors.append({'row': idx, 'reason': 'Missing English theory marks', 'row_data': row})
                continue
            if not language_subject or language_subject not in ['Kannada', 'Hindi', 'Sanskrit'] or language_theory is None:
                error_count += 1
                row_errors.append({'row': idx, 'reason': 'Missing or invalid language subject/theory', 'row_data': row})
                continue

            exam_type = str(row.get('exam_type', '')).strip() if row.get('exam_type') else None
            if not exam_type or exam_type not in ['JUT', 'JFT', 'Mid Term', 'Unit Test', 'Final Exam']:
                error_count += 1
                row_errors.append({'row': idx, 'reason': 'Missing or invalid exam_type (must be JUT, JFT, Mid Term, Unit Test, or Final Exam)', 'row_data': row})
                continue

            test_name = str(row.get('test_name', '')).strip() if row.get('test_name') and not pd.isna(row.get('test_name')) else None
            test_number = parse_value(row.get('test_number'))
            subject = str(row.get('subject', '')).strip() if row.get('subject') and not pd.isna(row.get('subject')) else None

            # Validate unit test fields
            if exam_type == 'Unit Test':
                if not test_name or not test_number or not subject:
                    error_count += 1
                    row_errors.append({'row': idx, 'reason': 'Unit Test requires test_name, test_number, and subject', 'row_data': row})
                    continue
                if subject not in ['English', 'Kannada', 'Hindi', 'Sanskrit', 'Physics', 'Chemistry', 'Maths', 'Biology', 'Computer Science']:
                    error_count += 1
                    row_errors.append({'row': idx, 'reason': 'Invalid subject for Unit Test', 'row_data': row})
                    continue
            else:
                # For non-unit tests, these should be None
                test_name = None
                test_number = None
                subject = None

            new_record = AcademicRecord(
                student_id=student_id_val,
                exam_type=exam_type,
                test_name=test_name,
                test_number=test_number,
                subject=subject,
                attendance_percentage=attendance_pct,
                academic_year=academic_year_val,
                english_theory=english_theory,
                language_subject=language_subject,
                language_theory=language_theory,
                physics_theory=parse_value(row.get('physics_theory')),
                physics_practical=parse_value(row.get('physics_practical')),
                chemistry_theory=parse_value(row.get('chemistry_theory')),
                chemistry_practical=parse_value(row.get('chemistry_practical')),
                maths_theory=parse_value(row.get('maths_theory')),
                biology_theory=parse_value(row.get('biology_theory')),
                biology_practical=parse_value(row.get('biology_practical')),
                computer_science_theory=parse_value(row.get('computer_science_theory')),
                computer_science_practical=parse_value(row.get('computer_science_practical')),
                behavior_score=parse_value(row.get('behavior_score')) or 0
            )
            db.session.add(new_record)
            success_count += 1
        except Exception as exc:
            error_count += 1
            row_errors.append({'row': idx, 'reason': f'Exception: {str(exc)}', 'row_data': row})
    
    db.session.commit()
    remove_preview_file(session.pop('marks_preview_file', None))
    
    result_summary = {
        'success': success_count,
        'errors': error_count,
        'message': f'Successfully added {success_count} mark records. {error_count} errors.',
        'row_errors': row_errors
    }
    return render_template('preview_data.html', data=preview_data, type='marks', result_summary=result_summary, import_complete=True)

@app.route('/edit_student_marks/<int:record_id>', methods=['GET', 'POST'])
def edit_student_marks(record_id):
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash("Unauthorized: Only Faculty or Admins can edit student marks.")
        return redirect(url_for('dashboard'))

    record = AcademicRecord.query.filter_by(record_id=record_id).first()
    if not record:
        flash('Record not found.')
        return redirect(url_for('view_student_marks'))

    student = Student.query.filter_by(student_id=record.student_id).first()
    if not student:
        flash('Student not found.')
        return redirect(url_for('view_student_marks'))

    if request.method == 'POST':
        try:
            exam_type = request.form.get('exam_type')
            if not exam_type or exam_type not in ['JUT', 'JFT', 'Mid Term', 'Unit Test', 'Final Exam']:
                flash('Invalid exam type.')
                return render_template('edit_student_marks.html', record=record, student=student)

            record.exam_type = exam_type

            # Handle unit test fields
            if exam_type == 'Unit Test':
                test_name = request.form.get('test_name')
                test_number = request.form.get('test_number')
                subject = request.form.get('subject')
                
                if not test_name or not test_number or not subject:
                    flash('Unit Test requires test name, number, and subject.')
                    return render_template('edit_student_marks.html', record=record, student=student)
                
                if subject not in ['English', 'Kannada', 'Hindi', 'Sanskrit', 'Physics', 'Chemistry', 'Maths', 'Biology', 'Computer Science']:
                    flash('Invalid subject for Unit Test.')
                    return render_template('edit_student_marks.html', record=record, student=student)
                
                record.test_name = test_name
                record.test_number = int(test_number)
                record.subject = subject
            else:
                record.test_name = None
                record.test_number = None
                record.subject = None

            record.attendance_percentage = float(request.form.get('attendance_percentage', record.attendance_percentage))
            record.english_theory = int(request.form.get('english_theory') or None) if request.form.get('english_theory') else None
            record.language_subject = request.form.get('language_subject') if request.form.get('language_subject') else None
            record.language_theory = int(request.form.get('language_theory') or None) if request.form.get('language_theory') else None

            if record.english_theory is None:
                flash('English marks are required.')
                return render_template('edit_student_marks.html', record=record, student=student)
            if not record.language_subject or record.language_subject not in ['Kannada', 'Hindi', 'Sanskrit'] or record.language_theory is None:
                flash('Please select one language subject and enter its marks.')
                return render_template('edit_student_marks.html', record=record, student=student)

            record.physics_theory = int(request.form.get('physics_theory') or None) if request.form.get('physics_theory') else None
            record.physics_practical = int(request.form.get('physics_practical') or None) if request.form.get('physics_practical') else None
            record.chemistry_theory = int(request.form.get('chemistry_theory') or None) if request.form.get('chemistry_theory') else None
            record.chemistry_practical = int(request.form.get('chemistry_practical') or None) if request.form.get('chemistry_practical') else None
            record.maths_theory = int(request.form.get('maths_theory') or None) if request.form.get('maths_theory') else None
            record.biology_theory = int(request.form.get('biology_theory') or None) if request.form.get('biology_theory') else None
            record.biology_practical = int(request.form.get('biology_practical') or None) if request.form.get('biology_practical') else None
            record.computer_science_theory = int(request.form.get('computer_science_theory') or None) if request.form.get('computer_science_theory') else None
            record.computer_science_practical = int(request.form.get('computer_science_practical') or None) if request.form.get('computer_science_practical') else None
            record.behavior_score = int(request.form.get('behavior_score', record.behavior_score or 0))

            db.session.commit()
            flash('Student marks updated successfully.')
            return redirect(url_for('view_student_marks'))
        except ValueError as e:
            flash(f'Invalid input: {str(e)}')
        except Exception as e:
            flash(f'Error updating record: {str(e)}')

    return render_template('edit_student_marks.html', record=record, student=student)

@app.route('/subject_performance/<int:student_id>')
def subject_performance(student_id):
    """View subject-wise performance"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return render_template('error_page.html', title='Student Not Found', message='The requested student record could not be found.', return_url=url_for('dashboard'))
    
    records = AcademicRecord.query.filter_by(student_id=student_id).all()
    
    if not records:
        return render_template('error_page.html', title='Performance Not Found', message='No performance records have been created for this student yet.', return_url=url_for('dashboard'))
    
    latest_record = records[-1]
    
    subjects = latest_record.subject_totals.copy()
    if student.combination == 'PCMB':
        subjects.pop('Computer Science', None)
    else:
        subjects.pop('Biology', None)

    subjects = {k: v for k, v in subjects.items() if v is not None}
    
    weakest_subject = min(subjects, key=subjects.get) if subjects else None
    strongest_subject = max(subjects, key=subjects.get) if subjects else None

    recommendations = []
    if weakest_subject:
        recommendations.append(f'Focus on improving {weakest_subject} with targeted practice.')

    if latest_record.attendance_percentage < 75:
        recommendations.append('Attend classes regularly and keep attendance above 75% to avoid academic risk.')
    else:
        recommendations.append('Your attendance is on track; maintain this consistency.')

    if latest_record.average_marks < 60:
        recommendations.append('Review core concepts and use extra practice tests to improve overall marks.')
    else:
        recommendations.append('Maintain your current study routine to keep the average marks strong.')

    if student.combination == 'PCMB':
        if 'Biology' in subjects and subjects.get('Biology', 0) < 60:
            recommendations.append('Biology needs more attention; focus on diagrams and chapter-wise revision.')
        else:
            recommendations.append('Continue strengthening Biology concepts to support your PCMB stream goals.')
    else:
        if 'Computer Science' in subjects and subjects.get('Computer Science', 0) < 60:
            recommendations.append('Python and programming practice is important for PCMC; work on coding examples and small projects.')
        else:
            recommendations.append('Continue improving Python skills through practice and project-based learning.')

    if weakest_subject and weakest_subject in ['Maths', 'Physics', 'Chemistry', 'Computer Science', 'Biology']:
        recommendations.append('Use active revision methods, such as questions and sample papers, to strengthen your weakest subject.')

    return render_template('subject_performance.html', 
                          student=student, 
                          record=latest_record,
                          subjects=subjects,
                          weakest_subject=weakest_subject,
                          strongest_subject=strongest_subject,
                          attendance=latest_record.attendance_percentage,
                          total_marks=latest_record.total_marks,
                          average_marks=latest_record.average_marks,
                          recommendations=recommendations)

@app.route('/overall_report')
def overall_report():
    """Generate comparative academic result analysis for two years"""
    if 'user_id' not in session or session.get('role') not in ['Faculty', 'Admin']:
        flash('Unauthorized: Only Faculty or Admins can view overall reports.')
        return redirect(url_for('dashboard'))
    
    # Get data for 2025 and 2026
    years_data = {}
    for year in [2025, 2026]:
        year_records = db.session.query(AcademicRecord).filter_by(academic_year=year).all()
        unique_students = set(record.student_id for record in year_records)
        
        # Calculate metrics
        total_students = len(unique_students)
        appeared = len(year_records)  # Number of academic records
        
        cleared_count = 0
        score_95_above = 0
        hundreds_count = 0
        
        for record in year_records:
            if record.percentage >= 60:  # Assuming 60% is passing
                cleared_count += 1
            if record.percentage >= 95:
                score_95_above += 1
            if record.total_marks >= 600:  # All subjects scoring 100
                hundreds_count += 1
        
        pass_percentage = (cleared_count / appeared * 100) if appeared > 0 else 0
        
        years_data[year] = {
            'total_students': total_students,
            'appeared': appeared,
            'cleared': cleared_count,
            'pass_percentage': pass_percentage,
            'score_95_above': score_95_above,
            'hundreds': hundreds_count
        }
    
    # Calculate differences
    report_data = []
    
    # Total Students
    report_data.append({
        'particular': 'Total Students',
        '2025': f"{years_data[2025]['total_students']} (100%)",
        '2026': f"{years_data[2026]['total_students']} (100%)",
        'increased': '',
        'decreased': '',
        'remarks': ''
    })
    
    # Appeared
    # 2025 Appeared % (Calculated based on 2025 totals, not hardcoded 100)
    appeared_2025_pct = (years_data[2025]['appeared'] / years_data[2025]['total_students'] * 100) if years_data[2025]['total_students'] > 0 else 0
    appeared_2026_pct = (years_data[2026]['appeared'] / years_data[2026]['total_students'] * 100) if years_data[2026]['total_students'] > 0 else 0
    inc_dec_appeared = appeared_2026_pct - appeared_2025_pct
    
    report_data.append({
        'particular': 'Appeared',
        '2025': f"{years_data[2025]['appeared']} ({appeared_2025_pct:.2f}%)",
        '2026': f"{years_data[2026]['appeared']} ({appeared_2026_pct:.2f}%)",
        'increased': f"{inc_dec_appeared:.2f}%" if inc_dec_appeared > 0 else '',
        'decreased': f"{abs(inc_dec_appeared):.2f}%" if inc_dec_appeared < 0 else '',
        'remarks': 'Change in appearance rate'
    })
    
    # Cleared
    cleared_2025_pct = (years_data[2025]['cleared'] / years_data[2025]['appeared'] * 100) if years_data[2025]['appeared'] > 0 else 0
    cleared_2026_pct = (years_data[2026]['cleared'] / years_data[2026]['appeared'] * 100) if years_data[2026]['appeared'] > 0 else 0
    inc_dec_cleared = cleared_2026_pct - cleared_2025_pct
    
    report_data.append({
        'particular': 'Cleared',
        '2025': f"{years_data[2025]['cleared']} ({cleared_2025_pct:.2f}%)",
        '2026': f"{years_data[2026]['cleared']} ({cleared_2026_pct:.2f}%)",
        'increased': f"{inc_dec_cleared:.2f}%" if inc_dec_cleared > 0 else '',
        'decreased': f"{abs(inc_dec_cleared):.2f}%" if inc_dec_cleared < 0 else '',
        'remarks': 'Percentage of students who cleared'
    })
    
    # Pass Percentage
    inc_dec_pass = years_data[2026]['pass_percentage'] - years_data[2025]['pass_percentage']
    
    report_data.append({
        'particular': 'Pass Percentage',
        '2025': f"{years_data[2025]['pass_percentage']:.2f}%",
        '2026': f"{years_data[2026]['pass_percentage']:.2f}%",
        'increased': f"{inc_dec_pass:.2f}%" if inc_dec_pass > 0 else '',
        'decreased': f"{abs(inc_dec_pass):.2f}%" if inc_dec_pass < 0 else '',
        'remarks': 'Overall pass rate'
    })
    
    # 95% and Above
    score_95_2025_pct = (years_data[2025]['score_95_above'] / years_data[2025]['appeared'] * 100) if years_data[2025]['appeared'] > 0 else 0
    score_95_2026_pct = (years_data[2026]['score_95_above'] / years_data[2026]['appeared'] * 100) if years_data[2026]['appeared'] > 0 else 0
    inc_dec_95 = score_95_2026_pct - score_95_2025_pct
    
    report_data.append({
        'particular': '95% and Above',
        '2025': f"{years_data[2025]['score_95_above']} ({score_95_2025_pct:.2f}%)",
        '2026': f"{years_data[2026]['score_95_above']} ({score_95_2026_pct:.2f}%)",
        'increased': f"{inc_dec_95:.2f}%" if inc_dec_95 > 0 else '',
        'decreased': f"{abs(inc_dec_95):.2f}%" if inc_dec_95 < 0 else '',
        'remarks': 'Distinction grade achievers'
    })
    
    # Number of Hundreds
    hundreds_2025_pct = (years_data[2025]['hundreds'] / years_data[2025]['appeared'] * 100) if years_data[2025]['appeared'] > 0 else 0
    hundreds_2026_pct = (years_data[2026]['hundreds'] / years_data[2026]['appeared'] * 100) if years_data[2026]['appeared'] > 0 else 0
    inc_dec_hundreds = hundreds_2026_pct - hundreds_2025_pct
    
    report_data.append({
        'particular': 'No. of Hundreds',
        '2025': f"{years_data[2025]['hundreds']} ({hundreds_2025_pct:.2f}%)",
        '2026': f"{years_data[2026]['hundreds']} ({hundreds_2026_pct:.2f}%)",
        'increased': f"{inc_dec_hundreds:.2f}%" if inc_dec_hundreds > 0 else '',
        'decreased': f"{abs(inc_dec_hundreds):.2f}%" if inc_dec_hundreds < 0 else '',
        'remarks': 'Perfect score achievers'
    })
    
    return render_template('overall_report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)