import mysql.connector
from werkzeug.security import generate_password_hash

# Corrected connection parameters
conn = mysql.connector.connect(
    host="localhost",      # Host only
    port=3306,             # Port separately
    user="root",
    password="root",
    database="student_performance_db"
)
cursor = conn.cursor()

# Process 1.0: Select users to update their credentials
cursor.execute("SELECT user_id, password_hash FROM users")
rows = cursor.fetchall()

for user_id, pwd in rows:
    # Check if the password is already hashed (scrypt/pbkdf2 hashes are long and start with 'scrypt:' or 'pbkdf2:')
    if pwd and not pwd.startswith(('scrypt:', 'pbkdf2:')):
        hashed = generate_password_hash(pwd)
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE user_id=%s",
            (hashed, user_id)
        )
        print(f"Updated user ID {user_id} to hashed password.")

conn.commit()
cursor.close()
conn.close()