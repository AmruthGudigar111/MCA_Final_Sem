================================================================================
                    CONFIGURATION GUIDE
================================================================================

This guide covers all configuration options for the Student Performance 
Prediction System.

================================================================================
DATABASE CONFIGURATION
================================================================================

File: app.py (lines ~30-45)

Current Configuration:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/student_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

To Update:
1. Open app.py
2. Locate SQLALCHEMY_DATABASE_URI
3. Replace with your credentials:
   Format: mysql+pymysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE

Examples:
- Local: mysql+pymysql://root:password@localhost/student_db
- Remote: mysql+pymysql://user:pass@192.168.1.10:3306/student_db
- Docker: mysql+pymysql://root:password@mysql_container/student_db

Connection Parameters:
- USERNAME: MySQL user name
- PASSWORD: MySQL password
- HOSTNAME: MySQL server address (localhost or IP)
- PORT: MySQL port (default 3306)
- DATABASE: Database name

================================================================================
FLASK CONFIGURATION
================================================================================

File: app.py

Key Settings:

1. Debug Mode:
   app.debug = True    # Enable for development
   app.debug = False   # Disable for production

2. Secret Key (for sessions):
   app.config['SECRET_KEY'] = 'your-secret-key-here'
   - Change this to a random string in production
   - Generate: python -c "import secrets; print(secrets.token_hex(32))"

3. Session Configuration:
   PERMANENT_SESSION_LIFETIME: 1800 seconds (30 minutes default)
   SESSION_COOKIE_SECURE: Set to True for HTTPS
   SESSION_COOKIE_HTTPONLY: Should be True

================================================================================
FILE UPLOAD CONFIGURATION
================================================================================

File: app.py (lines ~20-25)

Current Configuration:
```python
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
```

To Modify:

1. Change Upload Directory:
   UPLOAD_FOLDER = 'path/to/uploads'

2. Allowed File Types:
   ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

3. Maximum File Size:
   MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

Important: Ensure upload folder has write permissions
```bash
chmod -R 755 uploads/      # Linux/macOS
# Windows: Right-click → Properties → Security → Edit
```

================================================================================
MACHINE LEARNING CONFIGURATION
================================================================================

File: predict.py

Model Settings:

1. Random Forest Parameters:
   - n_estimators: 100 (number of trees)
   - random_state: 42 (for reproducibility)
   - To modify: Line ~43 in predict.py

2. Train-Test Split:
   - Test size: 0.2 (20% for testing)
   - To modify: Line ~28 in predict.py

3. Feature Weights (for risk calculation):
   - Attendance: 40%
   - Marks: 50%
   - Behavior: 10%
   - To modify: Line ~99 in predict.py

4. Risk Thresholds:
   - Low Risk: >= 75
   - Medium Risk: 55-74
   - High Risk: < 55
   - To modify: Lines ~101-102 in predict.py

5. Model Files:
   - Model: student_model.pkl
   - Scaler: scaler.pkl
   - Location: Project root directory

Retraining Model:
- Navigate to: /train_model (Admin only)
- Generates synthetic data automatically
- Takes ~10 seconds

================================================================================
STUDY PLAN CONFIGURATION
================================================================================

File: predict.py, Method: generate_study_plan()

Customizable Parameters:

1. Subject Performance Thresholds:
   - Weak Subject: < 60% (Line ~82)
   - Strong Subject: >= 60%

2. Priority Levels:
   - High Priority: < 40%
   - Medium Priority: 40-60%
   - To modify: Line ~87

3. Daily Study Hours:
   - Maximum: 4 hours (Line ~101)
   - Calculation: min(4, weak_count * 1.5)

4. Weak Subject Recommendations:
   - High Priority: 2-3 hours daily + tutoring
   - Medium Priority: 1-2 hours daily
   - To modify: Lines ~94-99

5. Study Plan Components:
   - Daily schedule
   - Monthly goals
   - Subject recommendations
   - Weak subject prioritization

================================================================================
APPLICATION ROUTES & ENDPOINTS
================================================================================

File: app.py

Core Routes Configuration:

Authentication Routes:
@app.route('/login', methods=['GET', 'POST'])          # User login
@app.route('/logout')                                   # User logout
@app.route('/forgot_password', methods=['GET', 'POST']) # Password recovery
@app.route('/reset_password/<token>', methods=['GET', 'POST'])

Management Routes:
@app.route('/manage_students')                          # Student list
@app.route('/manage_users')                             # User management
@app.route('/add_student', methods=['GET', 'POST'])     # Add student
@app.route('/edit_student/<int:student_id>')            # Edit student
@app.route('/add_user', methods=['GET', 'POST'])        # Add user

Academic Routes:
@app.route('/student_marks/<int:student_id>')           # View marks
@app.route('/edit_student_marks/<int:student_id>')      # Edit marks
@app.route('/upload_marks', methods=['GET', 'POST'])    # Bulk upload
@app.route('/attendance_form', methods=['GET', 'POST']) # Record attendance

Analytics Routes:
@app.route('/predictions')                              # Risk predictions
@app.route('/study_plan/<int:student_id>')              # Study plan
@app.route('/analytics')                                # Analytics dashboard
@app.route('/subject_performance')                      # Subject analysis

Upload Routes:
@app.route('/upload_students', methods=['GET', 'POST']) # Bulk student upload
@app.route('/upload_marks', methods=['GET', 'POST'])    # Bulk marks upload

To Add Custom Route:
```python
@app.route('/custom_route', methods=['GET', 'POST'])
def custom_function():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    # Your code here
    return render_template('template.html')
```

================================================================================
TEMPLATE CONFIGURATION
================================================================================

File: templates/ directory

Bootstrap CSS:
- All templates use Bootstrap 5
- Responsive design automatically applied
- Modify in: <link rel="stylesheet" href="...">

Navigation Bar:
- Located in all templates
- Roles shown in navbar
- Modify in template header

Flash Messages:
- Success: {% if get_flashed_messages() %}
- Error: Same container
- Modify in templates/base.html (if exists)

Form Validation:
- Client-side: HTML5 required attributes
- Server-side: app.py route validation
- Add validation in routes as needed

================================================================================
DATABASE SCHEMA CONFIGURATION
================================================================================

File: recreate_db.py

To Modify Database Schema:

1. Define Model in recreate_db.py:
```python
class NewModel(db.Model):
    __tablename__ = 'new_table'
    id = db.Column(db.Integer, primary_key=True)
    # Add columns
```

2. Run script:
   python recreate_db.py

3. WARNING: This DROPS and recreates all tables!
   - Backup database before running
   - All data will be lost

Tables Created:
- User: user_id, username, password_hash, full_name, role
- Student: student_id, reg_number, name, email, phone
- AcademicRecord: record_id, student_id, marks, attendance

================================================================================
SECURITY CONFIGURATION
================================================================================

Critical Settings:

1. Secret Key (app.py):
   - CHANGE from default before production
   - Generate random: python -c "import secrets; print(secrets.token_hex(32))"
   - Update: app.config['SECRET_KEY'] = 'new-key-here'

2. Password Policy:
   - Minimum length: 6 characters (in hashing.py)
   - Hashing: Werkzeug default (bcrypt)
   - Can be customized in change_user_password route

3. Session Security:
   - Timeout: 30 minutes (edit in app.py if needed)
   - Automatic logout on timeout
   - Cookie: HTTP-only (secure)

4. SQL Injection Prevention:
   - Using SQLAlchemy ORM (parameterized queries)
   - No raw SQL concatenation
   - Safe by default

5. Role-Based Access:
   - Implemented in route decorators
   - Check session['role'] before allowing action
   - Add checks to new routes as needed

6. File Upload Security:
   - File type validation (ALLOWED_EXTENSIONS)
   - Size limitation (MAX_FILE_SIZE)
   - Secure filename handling (secure_filename())
   - Random naming with UUID

To Add Authentication Check to Route:
```python
def admin_only_redirect():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized")
        return redirect(url_for('dashboard'))
    return None

@app.route('/admin_route')
def admin_route():
    redirect_response = admin_only_redirect()
    if redirect_response:
        return redirect_response
    # Safe to proceed
```

================================================================================
LOGGING CONFIGURATION (OPTIONAL)
================================================================================

To Add Logging:

1. Add to app.py (top):
```python
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

2. Log events:
```python
app.logger.info('User login: ' + username)
app.logger.error('Database error: ' + str(error))
```

Log Levels:
- DEBUG: Detailed diagnostics
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

================================================================================
PERFORMANCE TUNING
================================================================================

Database Optimization:
1. Add indexes to frequently searched columns
2. Archive old academic year records
3. Use pagination for large datasets (implement in app.py)

Caching:
1. Implement flask-caching for analytics data
2. Cache study plans for 24 hours
3. Cache predictions for 1 hour

Code Optimization:
1. Use bulk uploads (already implemented)
2. Lazy load relationships
3. Limit query results

Server Performance:
1. Use gunicorn for production: gunicorn -w 4 app:app
2. Implement load balancing for high traffic
3. Use CDN for static files

================================================================================
TROUBLESHOOTING CONFIGURATION ISSUES
================================================================================

Issue: "Can't connect to database"
Solution: Check SQLALCHEMY_DATABASE_URI in app.py
         Verify MySQL credentials and hostname

Issue: "File upload fails"
Solution: Check UPLOAD_FOLDER path exists
         Verify write permissions
         Check MAX_FILE_SIZE limit

Issue: "Model prediction not working"
Solution: Run /train_model route to train model
         Check student_model.pkl exists
         Verify predict.py has no syntax errors

Issue: "Template not found"
Solution: Check templates/ folder path
         Ensure template filename is correct
         Verify template syntax

================================================================================
For more help, refer to Readme.txt and INSTALLATION.md
================================================================================
