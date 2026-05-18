================================================================================
         STUDENT PERFORMANCE PREDICTION SYSTEM
================================================================================

PROJECT OVERVIEW
================================================================================
A comprehensive web-based application designed to predict student academic 
performance, manage student records, track attendance, and generate personalized 
AI-powered study plans. Built with Flask and machine learning capabilities.

KEY FEATURES
================================================================================
✓ User Authentication & Role-Based Access Control
  - Admin: Full system access
  - Faculty: Student management and analytics
  - Student: View performance and study plans
  - Parent: Track student progress

✓ Student Management
  - Bulk student import from CSV/Excel
  - Edit/update student information
  - Track student details and academic history

✓ Academic Records & Marks Management
  - Upload marks in bulk (JUT, JFT, Mid Term, Unit Tests, Final Exam)
  - Edit individual student marks
  - CSV templates for safe data entry
  - Automatic academic year tracking

✓ Attendance Management
  - Record and track attendance percentage
  - Associate with exam types/unit tests
  - Attendance-based performance prediction

✓ AI-Powered Predictions
  - Predict student risk levels (Low/Medium/High)
  - Risk prediction based on attendance, marks, and behavior
  - Machine learning model training with synthetic data

✓ Study Plans & Analytics
  - AI-generated personalized study plans
  - Identify weak and strong subjects
  - Daily study schedules and monthly goals
  - Comprehensive analytics dashboard
  - Subject-wise performance tracking

✓ Security
  - Password hashing with Werkzeug
  - Security questions for account recovery
  - Role-based authorization
  - Session management

PROJECT STRUCTURE
================================================================================
student_prediction_project/
├── app.py                    # Main Flask application & all routes
├── predict.py               # ML predictor & study plan generator
├── recreate_db.py           # Database schema setup script
├── requirements.txt         # Python dependencies
├── Readme.txt              # This file
│
├── templates/               # Jinja2 HTML templates
│   ├── login.html
│   ├── register_student.html
│   ├── register_parent.html
│   ├── add_user.html
│   ├── add_student.html
│   ├── dashboard.html
│   ├── manage_students.html
│   ├── manage_users.html
│   ├── student_marks.html
│   ├── edit_student_marks.html
│   ├── upload_marks.html
│   ├── upload_students.html
│   ├── attendance_form.html
│   ├── predictions.html
│   ├── study_plan.html
│   ├── analytics.html
│   ├── subject_performance.html
│   ├── overall_report.html
│   ├── search_student.html
│   ├── error_page.html
│   ├── change_user_password.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── security_question.html
│   └── preview_data.html
│
├── static/                  # Static files & utilities
│   └── hashing.py          # Password hashing utilities
│
├── uploads/                 # Uploaded files storage
│   ├── marks_template.csv   # Marks upload template
│   ├── student_template.csv # Students upload template
│   └── *.json              # Temporary uploaded data
│
└── csv_samples/             # Sample CSV files
    ├── bulk_marks.csv
    └── bulk_students.csv

INSTALLATION & SETUP
================================================================================

1. PREREQUISITES
   - Python 3.8 or higher
   - MySQL Server 5.7 or higher
   - pip (Python package manager)

2. INSTALLATION STEPS

   a) Clone or download the project:
      cd student_prediction_project

   b) Create a virtual environment:
      python -m venv venv
      
   c) Activate virtual environment:
      On Windows:  venv\Scripts\activate
      On Mac/Linux: source venv/bin/activate

   d) Install dependencies:
      pip install -r requirements.txt

   e) Configure database connection:
      Edit app.py and update database URL:
      - Line ~35: SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/db_name'
      
      Note: Ensure MySQL is running and database exists

   f) Initialize database schema:
      python recreate_db.py
      
      This will:
      - Create all required tables
      - Set up default admin user (username: admin, password: admin123)

   g) Start the Flask application:
      python app.py
      
      Server runs on: http://127.0.0.1:5000

3. FIRST LOGIN
   Default credentials:
   - Username: admin
   - Password: admin123
   
   IMPORTANT: Change admin password immediately after first login

DATABASE CONFIGURATION
================================================================================

MySQL Connection String Format:
mysql+pymysql://USERNAME:PASSWORD@HOSTNAME/DATABASE_NAME

Default Configuration (app.py line ~35):
mysql+pymysql://root:password@localhost/student_db

To change:
1. Open app.py
2. Locate SQLALCHEMY_DATABASE_URI
3. Update with your MySQL credentials
4. Run: python recreate_db.py

USAGE GUIDE
================================================================================

ADMIN WORKFLOW
-----------
1. Login with admin credentials
2. Add Faculty/Staff users (Manage Users)
3. Add students (Add Student or Bulk Upload)
4. Navigate to Dashboard

FACULTY WORKFLOW
-----------
1. Login with faculty credentials
2. View student list (Manage Students)
3. Upload marks (Upload Marks - use CSV template)
4. Record attendance (Attendance Form)
5. View analytics (Analytics)
6. Monitor risk predictions (Predictions)

STUDENT WORKFLOW
-----------
1. Login with student credentials
2. View dashboard
3. Check marks (Student Marks)
4. View study plans (Study Plans)
5. Monitor predictions (Predictions)

PARENT WORKFLOW
-----------
1. Login with parent credentials
2. Search for child (Search Student)
3. View student performance
4. Monitor study plans and predictions

CSV UPLOAD TEMPLATES
================================================================================

MARKS UPLOAD TEMPLATE (marks_template.csv):
Headers: student_id, student_name, subject_code, subject_name, exam_type, 
         marks, unit_test_number (optional)

Exam Types Supported:
- JUT (January Unit Test)
- JFT (January Full Test)
- Mid Term
- Unit Test
- Final Exam

Example:
student_id,student_name,subject_code,subject_name,exam_type,marks
101,John Doe,MAT001,Mathematics,Mid Term,85
102,Jane Smith,ENG001,English,Final Exam,92

STUDENT UPLOAD TEMPLATE (student_template.csv):
Headers: reg_number, name, email, phone, academic_year, class, 
         section, combination, date_of_birth

Example:
reg_number,name,email,phone,academic_year,class,section,combination
REG001,John Doe,john@example.com,9876543210,2024,12,A,Science
REG002,Jane Smith,jane@example.com,9876543211,2024,12,B,Commerce

MACHINE LEARNING MODEL
================================================================================

RISK PREDICTION MODEL
- Algorithm: Random Forest Classifier (100 trees)
- Features Used:
  * Attendance Percentage (40% weight)
  * Internal Marks (50% weight)
  * Behavior Score (10% weight)
  
- Risk Levels:
  * Low Risk: Score >= 75
  * Medium Risk: Score 55-74
  * High Risk: Score < 55

TRAINING & MODEL UPDATES
- Navigate to: /train_model (Admin only)
- Generates synthetic training data automatically
- Model saved locally as: student_model.pkl, scaler.pkl

STUDY PLAN GENERATION
- AI identifies weak and strong subjects
- Recommends daily study schedules
- Sets monthly improvement goals
- Prioritizes high-risk subjects

TROUBLESHOOTING
================================================================================

ERROR: MySQL Connection Failed
- Ensure MySQL server is running
- Verify credentials in app.py
- Check database exists: CREATE DATABASE student_db;

ERROR: Missing Tables
- Run: python recreate_db.py
- This recreates all database tables

ERROR: Template Not Found
- Ensure templates/ folder exists and contains all HTML files
- Check file paths are correct

ERROR: File Upload Failed
- Check uploads/ directory permissions
- Ensure uploads/ folder exists
- File should be CSV or Excel format

ERROR: Authentication Issues
- Clear browser cookies
- Delete session file if exists
- Try logging in again
- Use admin credentials to add new users

DEPENDENCIES & VERSIONS
================================================================================
Flask==3.0.0                  # Web framework
Flask-SQLAlchemy==3.1.1       # ORM
SQLAlchemy==2.0.23            # Database toolkit
PyMySQL==1.1.0                # MySQL driver
cryptography==41.0.7          # Encryption
Werkzeug==3.0.1               # WSGI utilities
scikit-learn==1.3.2           # Machine learning
pandas==2.1.3                 # Data analysis
numpy==1.26.2                 # Numerical computing
matplotlib==3.8.2             # Visualization
seaborn==0.13.0               # Statistical visualization
openpyxl==3.1.2               # Excel files
joblib==1.3.2                 # Serialization
python-dotenv==1.0.0          # Environment variables

PERFORMANCE OPTIMIZATION TIPS
================================================================================
1. Use bulk upload for large datasets (>100 students)
2. Update attendance in batches
3. Train ML model periodically for accuracy
4. Backup database regularly
5. Archive old academic year records

SECURITY RECOMMENDATIONS
================================================================================
✓ Change default admin password immediately
✓ Use strong passwords for all users
✓ Regularly update security questions
✓ Don't share admin credentials
✓ Use environment variables for sensitive data
✓ Enable HTTPS in production
✓ Implement rate limiting for login attempts
✓ Regular backups of database

API ENDPOINTS (INTERNAL)
================================================================================
/login                    - User login
/logout                   - User logout
/dashboard                - Main dashboard
/manage_students          - Student management
/manage_users             - User management
/upload_marks             - Bulk upload marks
/upload_students          - Bulk upload students
/student_marks/<id>       - View student marks
/edit_student_marks/<id>  - Edit marks
/attendance_form          - Record attendance
/predictions              - View predictions
/study_plan/<id>          - Generate study plan
/analytics                - View analytics
/train_model              - Train ML model (Admin)
/download_marks_template  - Download marks CSV template
/download_student_template - Download student CSV template

SUPPORT & DOCUMENTATION
================================================================================
For issues or feature requests, check:
1. The Troubleshooting section above
2. Application error messages
3. Browser console (F12 Developer Tools)
4. Flask debug mode output (terminal)

FUTURE ENHANCEMENTS
================================================================================
□ Mobile app version
□ Real-time notifications
□ Advanced analytics dashboard
□ Parent-teacher portal
□ Multi-language support
□ SMS/Email notifications
□ Advanced ML models (Neural Networks, XGBoost)
□ Customizable reports
□ API for third-party integration
□ Backup & restore functionality

VERSION HISTORY
================================================================================
v1.0.0 - Initial Release
- User authentication & role management
- Student management system
- Marks upload & tracking
- Risk prediction model
- Study plan generation
- Analytics dashboard
- Attendance tracking

LICENSE & DISCLAIMER
================================================================================
This software is provided as-is for educational purposes. Ensure all data 
is handled securely and complies with local data protection regulations.

================================================================================
Last Updated: May 2026
For installation help, refer to INSTALLATION & SETUP section above
================================================================================