================================================================================
                    INSTALLATION GUIDE - DETAILED
================================================================================

STEP 1: SYSTEM REQUIREMENTS
================================================================================
Operating System: Windows, macOS, or Linux
Python Version: 3.8 or higher
MySQL Version: 5.7 or higher
RAM: Minimum 2GB
Disk Space: Minimum 500MB

STEP 2: DOWNLOAD & SETUP
================================================================================

1. Navigate to project directory:
   cd student_prediction_project

2. Create Python Virtual Environment:
   Windows:
   python -m venv venv
   
   macOS/Linux:
   python3 -m venv venv

3. Activate Virtual Environment:
   Windows:
   venv\Scripts\activate
   
   macOS/Linux:
   source venv/bin/activate
   
   You should see (venv) in your terminal prompt

STEP 3: INSTALL DEPENDENCIES
================================================================================

1. Upgrade pip:
   python -m pip install --upgrade pip

2. Install requirements:
   pip install -r requirements.txt

3. Verify installation:
   python -c "import flask; import pandas; print('Installation successful!')"

STEP 4: DATABASE SETUP
================================================================================

1. Install and Start MySQL Server:
   Windows: Start MySQL from Services or Start Menu
   macOS: brew services start mysql
   Linux: sudo service mysql start

2. Create MySQL Database:
   Open MySQL Command Line:
   
   CREATE DATABASE student_db;
   CREATE USER 'student_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON student_db.* TO 'student_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;

3. Configure Database in app.py:
   Open app.py
   Find line: SQLALCHEMY_DATABASE_URI = 
   Update to: 'mysql+pymysql://student_user:secure_password@localhost/student_db'
   
   Save the file

STEP 5: INITIALIZE DATABASE SCHEMA
================================================================================

Run the database setup script:
python recreate_db.py

Expected output:
- Database tables created
- Default admin user created (username: admin, password: admin123)
- System ready message

If you see errors:
1. Check MySQL is running
2. Verify database credentials in app.py
3. Ensure database user has privileges

STEP 6: START THE APPLICATION
================================================================================

1. Run Flask application:
   python app.py

2. Expected output:
   WARNING in app.run_simple (line XXX)
   Running on http://127.0.0.1:5000
   Press CTRL+C to quit
   
3. Open web browser:
   Visit: http://localhost:5000
   Or: http://127.0.0.1:5000

STEP 7: FIRST LOGIN
================================================================================

1. Default Admin Credentials:
   Username: admin
   Password: admin123

2. IMPORTANT - Change Admin Password:
   - Click on Manage Users
   - Find admin user
   - Click Change Password
   - Set a new secure password

3. Add Faculty Users:
   - As Admin, go to Add User
   - Create faculty accounts
   - Share credentials securely

STEP 8: TROUBLESHOOTING INSTALLATION
================================================================================

Problem: "ModuleNotFoundError: No module named 'flask'"
Solution: Ensure virtual environment is activated
         Run: pip install -r requirements.txt

Problem: "ERROR 1045: Access denied for user 'root'@'localhost'"
Solution: Check MySQL credentials in app.py
         Ensure database user exists with correct password
         Run: mysql -u root -p (test connection)

Problem: "Can't connect to MySQL server on 'localhost'"
Solution: Check MySQL service is running
         Windows: mysql -u root -p (should connect)
         macOS: brew services start mysql
         Linux: sudo service mysql start

Problem: "ModuleNotFoundError: No module named 'mysql'"
Solution: Install PyMySQL: pip install PyMySQL

Problem: "Template not found" error
Solution: Check templates/ folder exists in project root
         Ensure all HTML files are present
         Check file permissions

Problem: "Permission denied" on uploads/
Solution: Ensure uploads/ folder has write permissions
         Windows: Right-click → Properties → Security → Edit
         Linux/macOS: chmod -R 755 uploads/

STEP 9: PRODUCTION DEPLOYMENT (Optional)
================================================================================

For production use:
1. Set FLASK_ENV=production in app.py
2. Use Gunicorn: pip install gunicorn
3. Run: gunicorn -w 4 app:app
4. Use Nginx as reverse proxy
5. Enable HTTPS with SSL certificate
6. Update SECRET_KEY in app.py to secure random value

STEP 10: BACKUP & MAINTENANCE
================================================================================

Daily Backups:
mysqldump -u root -p student_db > backup_$(date +%Y%m%d).sql

Restore from Backup:
mysql -u root -p student_db < backup_20240515.sql

Clean Old Files:
python -c "import os; [os.remove(f) for f in os.listdir('uploads/') if f.endswith('.json')]"

STEP 11: POST-INSTALLATION CHECKLIST
================================================================================
□ Virtual environment created and activated
□ All dependencies installed (pip list shows all packages)
□ MySQL server installed and running
□ Database created with proper user permissions
□ app.py updated with correct database credentials
□ Database tables created (recreate_db.py executed)
□ Application starts without errors (python app.py)
□ Can access http://localhost:5000 in browser
□ Login works with admin/admin123
□ Can access Dashboard after login
□ Default admin password changed

If all checkboxes are ticked, installation is complete!

STEP 12: QUICK START AFTER INSTALLATION
================================================================================

Every time you want to run the application:

1. Activate virtual environment:
   Windows: venv\Scripts\activate
   macOS/Linux: source venv/bin/activate

2. Start MySQL (if not already running)

3. Run application:
   python app.py

4. Access in browser:
   http://localhost:5000

5. Stop application:
   Press CTRL+C in terminal

================================================================================
For further help, refer to Readme.txt in the project root
================================================================================
