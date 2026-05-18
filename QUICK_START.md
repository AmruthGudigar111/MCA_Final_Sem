================================================================================
                    QUICK REFERENCE GUIDE
================================================================================

Common Commands & Tasks

================================================================================
STARTING THE APPLICATION
================================================================================

1. Activate virtual environment:
   Windows: venv\Scripts\activate
   macOS/Linux: source venv/bin/activate

2. Start Flask app:
   python app.py

3. Access application:
   http://localhost:5000

4. Stop application:
   Press CTRL+C in terminal

================================================================================
DATABASE OPERATIONS
================================================================================

Recreate Database:
python recreate_db.py

Backup Database:
mysqldump -u root -p student_db > backup_$(date +%Y%m%d).sql

Restore Database:
mysql -u root -p student_db < backup_20240515.sql

Connect to MySQL:
mysql -u root -p
USE student_db;
SHOW TABLES;

Drop Database (WARNING - Deletes all data):
DROP DATABASE student_db;

================================================================================
USER MANAGEMENT - ADMIN TASKS
================================================================================

Default Login:
Username: admin
Password: admin123

Add New Faculty User:
1. Login as admin
2. Go to Manage Users → Add User
3. Fill form:
   - Username: unique_name
   - Full Name: John Doe
   - Role: Faculty
   - Security Question: Select one
   - Security Answer: Enter answer
4. Click Add User

Change Admin Password:
1. Manage Users
2. Find admin
3. Click Change Password
4. Enter new password

Add Multiple Users:
Add users one by one (see above)
Or import CSV with admin role

================================================================================
STUDENT MANAGEMENT
================================================================================

Add Single Student:
1. Go to Add Student
2. Fill form:
   - Registration: REG001
   - Name: John Doe
   - Email: john@example.com
   - Phone: 9876543210
   - Academic Year: 2024
   - Class: 12
   - Combination: Science
3. Click Add

Bulk Upload Students:
1. Go to Upload Students
2. Download template (CSV)
3. Fill template with student data
4. Upload file
5. Verify preview
6. Click Import

Edit Student:
1. Manage Students
2. Click Edit button
3. Update fields
4. Click Update

Search Student:
1. Search Student page
2. Enter student name or reg number
3. View results
4. Click to view details

================================================================================
MARKS & ACADEMIC RECORDS
================================================================================

Upload Marks Bulk:
1. Go to Upload Marks
2. Download marks template (CSV)
3. Fill with student marks:
   - student_id: 101
   - subject_code: MAT001
   - subject_name: Mathematics
   - exam_type: Mid Term or Final Exam or JUT, etc.
   - marks: 85
4. Upload file
5. Verify data
6. Click Import

Edit Student Marks:
1. Manage Students
2. Click student name
3. Click Edit Marks
4. Update marks
5. Select exam type
6. Click Update

View Student Marks:
1. Manage Students
2. Click student name
3. View all marks by exam type
4. See calculated totals

Supported Exam Types:
- JUT (January Unit Test)
- JFT (January Full Test)
- Mid Term
- Unit Test
- Final Exam

================================================================================
ATTENDANCE & BEHAVIOR TRACKING
================================================================================

Record Attendance:
1. Go to Attendance Form
2. Select student
3. Enter:
   - Attendance Percentage: 85
   - Exam Type: Mid Term (optional)
   - Behavior Score: 8/10
4. Click Submit

View Attendance:
1. Student Marks page
2. See attendance percentage
3. See associated exam type

Update Attendance:
1. Edit Student Marks
2. Update attendance percentage
3. Click Update

================================================================================
PREDICTIONS & RISK ANALYSIS
================================================================================

View Risk Predictions:
1. Go to Predictions
2. See all students with risk levels:
   - Low Risk (green)
   - Medium Risk (yellow)
   - High Risk (red)
3. Confidence score shown
4. Sort by risk level

Train ML Model:
1. Admin only: /train_model
2. Generates synthetic data
3. Trains Random Forest model
4. Takes ~10 seconds
5. Accuracy score shown

Force Retrain Model:
1. Delete: student_model.pkl
2. Delete: scaler.pkl
3. Go to /train_model
4. Model will be retrained

Check Prediction Accuracy:
1. Go to Predictions
2. Verify risk levels match student performance
3. High Risk students should have low marks
4. Low Risk students should have high marks

================================================================================
STUDY PLANS
================================================================================

Generate Study Plan:
1. Go to Manage Students
2. Click student name
3. Click Generate Study Plan
4. Or: Go to /study_plan/student_id directly

View Study Plan:
1. See weak subjects (prioritized)
2. See strong subjects
3. Review daily schedule
4. Check monthly goals
5. Read recommendations

Components of Study Plan:
- Weak Subjects: Focus areas
- Strong Subjects: Maintain performance
- Daily Schedule: Morning & evening study times
- Recommendations: Subject-specific guidance
- Monthly Goals: Improvement targets

Export Study Plan:
Currently: View only (can screenshot/print)
Future: PDF export coming

================================================================================
ANALYTICS & REPORTING
================================================================================

View Analytics:
1. Go to Analytics (Faculty/Admin only)
2. See performance metrics:
   - Student name
   - Attendance
   - Average marks
   - Classification (Pass/Fail)
   - Behavior score
3. Sort by any column

Subject Performance Analysis:
1. Go to Subject Performance
2. Select subject
3. See student marks
4. Identify weak performers
5. Plan interventions

Overall Report:
1. Go to Overall Report
2. See statistics:
   - Total students
   - Pass/Fail rate
   - Average attendance
   - Top performers
   - Risk distribution

Download Report:
- Screenshots: Press PrtScn or use browser tools
- PDF: Use browser Print → Save as PDF
- CSV: Export functionality (coming in v1.1)

================================================================================
TROUBLESHOOTING QUICK FIXES
================================================================================

App Won't Start:
1. Check MySQL running: mysql -u root -p
2. Activate venv: source venv/bin/activate (or Windows equivalent)
3. Check Python syntax: python -m py_compile app.py
4. Reinstall: pip install -r requirements.txt

Login Not Working:
1. Clear browser cookies: CTRL+SHIFT+Delete
2. Close and reopen browser
3. Verify database has users: mysql → SELECT * FROM user;
4. Try admin/admin123

Can't Upload File:
1. Check file format: CSV or XLSX only
2. Check file size: < 16MB
3. Verify headers match template
4. Check uploads/ folder exists

Database Connection Error:
1. Start MySQL: mysql -u root -p
2. Check credentials in app.py
3. Create database: CREATE DATABASE student_db;
4. Verify user: mysql -u root -p student_db

Model Not Predicting:
1. Train model: /train_model route
2. Check files exist: student_model.pkl, scaler.pkl
3. Verify predict.py has no errors
4. Restart app: python app.py

Template Error:
1. Check file exists: templates/filename.html
2. Verify syntax: Python -m py_compile
3. Check permissions: read access
4. Restart Flask app

================================================================================
FILE PATHS REFERENCE
================================================================================

Important Locations:
- Database config: app.py (line ~35)
- Models: app.py (database models)
- ML predictor: predict.py
- Database setup: recreate_db.py
- Templates: templates/ directory
- Uploads: uploads/ directory
- Static files: static/ directory

Key Files to Backup:
- app.py (application code)
- predict.py (ML code)
- requirements.txt (dependencies)
- Database: student_db (MySQL)

Model Files:
- student_model.pkl (Random Forest model)
- scaler.pkl (Feature scaler)

================================================================================
SECURITY REMINDERS
================================================================================

Do's:
✓ Change default admin password immediately
✓ Use strong passwords (8+ characters)
✓ Back up database regularly
✓ Keep Python packages updated
✓ Use HTTPS in production
✓ Keep secret key confidential

Don'ts:
✗ Share admin credentials
✗ Upload sensitive files to public directories
✗ Use default passwords
✗ Commit .env files to version control
✗ Share database passwords in emails
✗ Disable security features

================================================================================
USEFUL LINKS
================================================================================

Documentation Files:
- Readme.txt: Project overview
- INSTALLATION.md: Detailed setup
- CONFIG.md: Configuration guide
- CHANGELOG.md: Version history

Online Resources:
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- scikit-learn: https://scikit-learn.org/
- Bootstrap: https://getbootstrap.com/

Common Issues & Solutions:
- Flask Debugging: https://flask.palletsprojects.com/errorhandling/
- MySQL Help: https://dev.mysql.com/doc/
- Python Packages: https://pypi.org/

================================================================================
KEYBOARD SHORTCUTS
================================================================================

Browser:
- F12: Developer Tools
- CTRL+Shift+Delete: Clear cookies
- CTRL+L: Address bar
- CTRL+P: Print page

Terminal:
- CTRL+C: Stop running app
- CTRL+L: Clear terminal
- Arrow Up: Previous command
- Tab: Autocomplete

Windows Only:
- CMD: Open Command Prompt
- CTRL+Alt+T: Terminal (may vary)

================================================================================
QUICK CHECKLIST FOR NEW INSTALLATION
================================================================================

□ Python 3.8+ installed
□ MySQL server installed & running
□ Virtual environment created
□ Dependencies installed (pip install -r requirements.txt)
□ Database created
□ app.py configured with DB credentials
□ recreate_db.py executed
□ Application starts (python app.py)
□ Can access http://localhost:5000
□ Admin login works
□ Admin password changed
□ Can access dashboard
□ Can view students
□ Can upload marks
□ Predictions working

If all checked, system is ready to use!

================================================================================
For detailed information, see the documentation files above
================================================================================
