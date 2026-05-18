================================================================================
                    PROJECT ARCHITECTURE & STRUCTURE
================================================================================

SYSTEM ARCHITECTURE OVERVIEW
================================================================================

The Student Performance Prediction System is built using a 3-tier 
architecture pattern:

1. PRESENTATION TIER (Frontend)
   - Jinja2 Templates (HTML)
   - Bootstrap 5 CSS Framework
   - HTML Forms for user input
   - Responsive design

2. APPLICATION TIER (Backend)
   - Flask Web Framework
   - Route handlers (views)
   - Business logic
   - Session management
   - Authentication & Authorization

3. DATA TIER (Database & ML)
   - MySQL Database
   - SQLAlchemy ORM
   - ML Model (scikit-learn)
   - File storage (uploads)

================================================================================
DETAILED DIRECTORY STRUCTURE
================================================================================

student_prediction_project/
│
├── Core Application Files
│   ├── app.py                   [~1100 lines]
│   │   ├── Flask app initialization
│   │   ├── Database configuration
│   │   ├── Route handlers (50+ routes)
│   │   ├── Authentication logic
│   │   ├── User management routes
│   │   ├── Student management routes
│   │   ├── Marks upload & editing routes
│   │   ├── Attendance tracking routes
│   │   ├── Analytics routes
│   │   ├── Prediction routes
│   │   ├── Study plan generation route
│   │   └── Utility functions
│   │
│   ├── predict.py               [~170 lines]
│   │   ├── StudentPerformancePredictor class
│   │   ├── Model training (train_model)
│   │   ├── Risk prediction (predict_risk)
│   │   ├── Sample data generation (generate_sample_data)
│   │   ├── Study plan generation (generate_study_plan)
│   │   ├── Model persistence (joblib)
│   │   └── ML pipeline
│   │
│   ├── recreate_db.py           [~150 lines]
│   │   ├── Database initialization
│   │   ├── Schema definition
│   │   ├── Table creation
│   │   ├── Default data seeding
│   │   └── Admin user creation
│   │
│   ├── requirements.txt          [14 packages]
│   │   ├── Flask 3.0.0
│   │   ├── SQLAlchemy 2.0.23
│   │   ├── scikit-learn 1.3.2
│   │   ├── pandas 2.1.3
│   │   ├── numpy 1.26.2
│   │   ├── And others...
│   │
│   └── Readme.txt               [Main documentation]
│
├── Configuration & Documentation
│   ├── .env.example             [Environment variables template]
│   ├── CONFIG.md                [Configuration guide]
│   ├── INSTALLATION.md          [Installation instructions]
│   ├── CHANGELOG.md             [Version history]
│   ├── QUICK_START.md           [Quick reference]
│   ├── .gitignore               [Git ignore rules]
│   ├── PROJECT_STRUCTURE.md     [This file]
│   └── Readme.txt               [Project overview]
│
├── templates/                   [25+ HTML templates]
│   ├── Authentication Pages
│   │   ├── login.html
│   │   ├── register_student.html
│   │   ├── register_parent.html
│   │   ├── forgot_password.html
│   │   ├── reset_password.html
│   │   ├── security_question.html
│   │   └── change_user_password.html
│   │
│   ├── Dashboard & Navigation
│   │   ├── dashboard.html       [Main dashboard]
│   │   ├── error_page.html      [Error handling]
│   │   └── preview_data.html    [Data preview]
│   │
│   ├── User Management
│   │   ├── add_user.html
│   │   ├── manage_users.html
│   │   └── change_user_password.html
│   │
│   ├── Student Management
│   │   ├── add_student.html
│   │   ├── edit_student.html
│   │   ├── manage_students.html
│   │   └── search_student.html
│   │
│   ├── Academic Records & Marks
│   │   ├── upload_marks.html    [Bulk upload]
│   │   ├── upload_students.html [Bulk student upload]
│   │   ├── student_marks.html   [View marks]
│   │   ├── edit_student_marks.html [Edit marks]
│   │   └── preview_data.html    [Upload preview]
│   │
│   ├── Attendance & Behavior
│   │   └── attendance_form.html [Attendance tracking]
│   │
│   ├── Predictions & Analysis
│   │   ├── predictions.html     [Risk predictions]
│   │   ├── study_plan.html      [AI study plans]
│   │   ├── analytics.html       [Dashboard analytics]
│   │   ├── subject_performance.html
│   │   └── overall_report.html  [Summary report]
│   │
│   └── Other Pages
│       └── Various supporting templates
│
├── static/                      [Static resources]
│   └── hashing.py              [Password hashing utilities]
│
├── uploads/                     [File uploads storage]
│   ├── marks_template.csv      [Marks upload template]
│   ├── student_template.csv    [Student upload template]
│   ├── *.json                  [Temporary data files]
│   └── *.csv                   [Uploaded CSV files]
│
└── csv_samples/                 [Sample CSV files]
    ├── bulk_marks.csv          [Sample marks data]
    └── bulk_students.csv       [Sample student data]

================================================================================
DATABASE SCHEMA
================================================================================

TABLE: user
├── user_id (PK)
├── username (UNIQUE)
├── password_hash
├── full_name
├── role (Admin/Faculty/Student/Parent)
├── security_question
├── security_answer
└── created_at

TABLE: student
├── student_id (PK)
├── reg_number (UNIQUE)
├── name
├── email
├── phone
├── academic_year
├── class
├── section
├── combination (Science/Commerce/Arts)
├── date_of_birth
└── created_at

TABLE: academic_record
├── record_id (PK)
├── student_id (FK)
├── subject_code
├── subject_name
├── exam_type (JUT/JFT/Mid Term/Unit Test/Final Exam)
├── marks
├── attendance_percentage
├── behavior_score
├── unit_test_number
├── subject_totals (JSON)
├── total_marks
├── average_marks
├── percentage
├── classification (Pass/Fail)
├── academic_year
└── created_at

================================================================================
KEY APPLICATION COMPONENTS
================================================================================

AUTHENTICATION SYSTEM
├── Password hashing (Werkzeug)
├── Session management (Flask sessions)
├── Role-based access control (4 roles)
├── Security questions for recovery
└── Login/logout functionality

USER MANAGEMENT
├── Add users (with role assignment)
├── Edit user details
├── Change password
├── Delete users (soft delete recommended)
└── Security question management

STUDENT MANAGEMENT
├── Add individual students
├── Bulk import from CSV/Excel
├── Edit student information
├── Search functionality
├── Student profile view
└── Academic year tracking

ACADEMIC RECORDS
├── Single mark entry
├── Bulk mark upload
├── Exam type support (5 types)
├── Subject-wise tracking
├── Attendance percentage
├── Behavior scoring
├── Unit test association
└── Mark editing

MACHINE LEARNING
├── Random Forest Classifier (100 trees)
├── Feature scaling (StandardScaler)
├── Risk level prediction (3 levels)
├── Model training with synthetic data
├── Model persistence (joblib)
├── Prediction confidence scores
└── Accuracy metrics

STUDY PLAN GENERATION
├── Weak subject identification
├── Strong subject recognition
├── Priority assignment
├── Daily schedule generation
├── Monthly goals creation
├── Personalized recommendations
└── Performance-based categorization

ANALYTICS & REPORTING
├── Performance dashboard
├── Subject-wise analysis
├── Risk distribution
├── Attendance patterns
├── Pass/fail statistics
├── Top performer identification
└── Behavioral analysis

FILE MANAGEMENT
├── CSV upload (marks & students)
├── Excel upload support
├── File validation
├── Size limitation
├── Secure filename handling
├── Template download
└── Preview functionality

================================================================================
DATA FLOW ARCHITECTURE
================================================================================

USER AUTHENTICATION FLOW:
1. User enters credentials (login.html)
2. Request → app.py (/login route)
3. Verify against database (User table)
4. Check password hash (Werkzeug)
5. Create session
6. Redirect to dashboard

MARKS UPLOAD FLOW:
1. User downloads template (CSV)
2. Fills template with marks data
3. Uploads file (upload_marks.html)
4. Request → app.py (/upload_marks)
5. Validate file format & content
6. Preview data (preview_data.html)
7. User confirms import
8. Insert into academic_record table
9. Redirect to student marks view

PREDICTION FLOW:
1. User views predictions page
2. Request → app.py (/predictions)
3. Fetch student records from database
4. For each student:
   a. Extract features (attendance, marks, behavior)
   b. Call predict.py (predict_risk)
   c. Load model & scaler
   d. Scale features
   e. Get prediction & confidence
5. Return results to template
6. Render predictions.html

STUDY PLAN FLOW:
1. User requests study plan for student
2. Request → app.py (/study_plan/<id>)
3. Fetch student records
4. Call predict.py (generate_study_plan)
5. Analyze subject performance
6. Generate recommendations
7. Create daily schedule
8. Set monthly goals
9. Return to study_plan.html

================================================================================
SECURITY ARCHITECTURE
================================================================================

AUTHENTICATION LAYER:
- Password hashing: Werkzeug (bcrypt-based)
- Session management: Flask secure sessions
- Login required decorators: On protected routes
- Role-based access: Check session['role']

DATA PROTECTION:
- SQL Injection Prevention: SQLAlchemy ORM
- XSS Prevention: Jinja2 auto-escaping
- CSRF Protection: Not implemented (add in production)
- File Upload Security: 
  * Type validation (ALLOWED_EXTENSIONS)
  * Size limit (MAX_FILE_SIZE)
  * Secure naming (secure_filename + UUID)

ACCESS CONTROL:
- Admin: Full system access
- Faculty: Student management, analytics
- Student: View own performance
- Parent: View child's performance

ENCRYPTION:
- Passwords: One-way hash (not recoverable)
- Database connection: Via MySQL connection string
- Session data: Flask session (server-side)

================================================================================
TECHNOLOGY STACK
================================================================================

BACKEND:
- Language: Python 3.8+
- Framework: Flask 3.0.0
- ORM: SQLAlchemy 2.0.23
- Database: MySQL 5.7+
- Driver: PyMySQL 1.1.0

MACHINE LEARNING:
- Library: scikit-learn 1.3.2
- Algorithm: Random Forest
- Data Processing: pandas 2.1.3, numpy 1.26.2
- Model Serialization: joblib 1.3.2

SECURITY:
- Password Hashing: Werkzeug 3.0.1
- Encryption: cryptography 41.0.7

FRONTEND:
- Template Engine: Jinja2
- CSS Framework: Bootstrap 5
- Forms: HTML5 with validation

FILE HANDLING:
- CSV: Built-in Python csv module
- Excel: openpyxl 3.1.2
- JSON: Built-in Python json module

VISUALIZATION:
- matplotlib 3.8.2
- seaborn 0.13.0

UTILITIES:
- python-dotenv 1.0.0 (environment variables)

================================================================================
DEPLOYMENT ARCHITECTURE
================================================================================

DEVELOPMENT:
- Local machine
- Flask development server (debug mode)
- SQLite or local MySQL
- Single instance

PRODUCTION (RECOMMENDED):
- Gunicorn/uWSGI application server
- Nginx reverse proxy
- MySQL database server
- SSL/TLS encryption
- Firewall & security groups
- Regular backups

CLOUD DEPLOYMENT:
- AWS: EC2 + RDS MySQL
- Google Cloud: Compute Engine + Cloud SQL
- Azure: App Service + Database
- Docker containerization (future)

================================================================================
SCALABILITY CONSIDERATIONS
================================================================================

HORIZONTAL SCALING:
- Implement load balancer (nginx)
- Use database connection pooling
- Cache study plans & predictions
- Archive old academic records
- Use CDN for static files

VERTICAL SCALING:
- Increase server RAM
- Upgrade database resources
- Optimize queries with indexes
- Implement pagination

OPTIMIZATION:
- Database indexing on frequently searched columns
- Query optimization
- Caching layer (Redis/Memcached)
- Lazy loading of relationships
- Asynchronous task processing (Celery)

================================================================================
MONITORING & MAINTENANCE
================================================================================

LOGGING:
- Application logs: app.log
- Database queries: Enable logging
- Error tracking: Flask error handlers
- User activity: Login/logout tracking

BACKUP STRATEGY:
- Daily database backups
- Version control (Git)
- Configuration backup (.env)
- Model file backup (student_model.pkl)

PERFORMANCE MONITORING:
- Response time tracking
- Query performance
- CPU & memory usage
- Disk space monitoring

SECURITY MONITORING:
- Failed login attempts
- Unauthorized access attempts
- File upload validation
- SQL injection attempts (None, using ORM)

================================================================================
EXTENSION POINTS (For Future Development)
================================================================================

FEATURES TO ADD:
1. Email notifications
2. SMS alerts
3. PDF report generation
4. Mobile app (React Native/Flutter)
5. REST API
6. Advanced ML models
7. Real-time notifications
8. Parent-teacher meetings portal
9. Video call integration
10. Customizable workflows

CODE EXTENSION AREAS:
- Add new routes in app.py
- Add new templates in templates/
- Add new ML models in predict.py
- Add new database tables in recreate_db.py
- Add new API endpoints
- Add new security features

DATABASE EXTENSION:
- Add audit logging table
- Add notification table
- Add meeting scheduling table
- Add document storage table
- Add feedback table

================================================================================
TESTING STRATEGY (Recommended)
================================================================================

UNIT TESTING:
- Test ML predictor functions
- Test database models
- Test authentication functions
- Use pytest framework

INTEGRATION TESTING:
- Test route handlers
- Test database operations
- Test file uploads
- Test authentication flow

LOAD TESTING:
- Test with 100+ concurrent users
- Measure response times
- Identify bottlenecks
- Use Apache JMeter or Locust

SECURITY TESTING:
- SQL injection tests
- XSS vulnerability tests
- CSRF protection tests
- Authentication bypass tests

================================================================================
VERSION CONTROL & DEPLOYMENT
================================================================================

GIT WORKFLOW:
- Main branch: Production code
- Develop branch: Development code
- Feature branches: New features
- Hotfix branches: Bug fixes

DEPLOYMENT PROCESS:
1. Commit code to feature branch
2. Create pull request
3. Code review
4. Merge to develop
5. Test on staging
6. Merge to main
7. Deploy to production
8. Monitor for errors

CI/CD PIPELINE (Recommended):
- GitHub Actions / GitLab CI
- Automated testing
- Code quality checks (SonarQube)
- Automated deployment

================================================================================
For detailed configuration, see CONFIG.md
For installation steps, see INSTALLATION.md
For quick reference, see QUICK_START.md
================================================================================
