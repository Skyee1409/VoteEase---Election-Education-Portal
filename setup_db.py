"""
VoteEase — Database Setup Script
Run this once to create the database and tables.
Usage: python setup_db.py
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Connect WITHOUT specifying database first (to create it)
print("🔌 Connecting to MySQL...")
try:
    conn = mysql.connector.connect(
        host     = os.environ.get('DB_HOST', 'localhost'),
        user     = os.environ.get('DB_USER', 'root'),
        password = os.environ.get('DB_PASSWORD', ''),
    )
    print("✅ Connected to MySQL successfully!")
except mysql.connector.Error as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Make sure:")
    print("   1. XAMPP is running (MySQL service is ON)")
    print("   2. DB_PASSWORD in .env is correct")
    exit(1)

cursor = conn.cursor()

# ── Create Database ────────────────────────────────────────
DB_NAME = os.environ.get('DB_NAME', 'voteease_db')
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
cursor.execute(f"USE `{DB_NAME}`")
print(f"✅ Database '{DB_NAME}' ready!")

# ── Create voters table ────────────────────────────────────
cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        voter_id     VARCHAR(20)  UNIQUE NOT NULL,
        full_name    VARCHAR(100) NOT NULL,
        dob          DATE         NOT NULL,
        gender       ENUM('Male','Female','Other') NOT NULL,
        aadhaar      VARCHAR(12)  UNIQUE NOT NULL,
        address      TEXT         NOT NULL,
        email        VARCHAR(100),
        phone        VARCHAR(15),
        registered_at DATETIME   DEFAULT CURRENT_TIMESTAMP
    )
""")
print("✅ Table 'voters' created!")

# ── Create notifications table ─────────────────────────────
cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        email        VARCHAR(100),
        phone        VARCHAR(15),
        subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_email_phone (email, phone)
    )
""")
print("✅ Table 'notifications' created!")

conn.close()
print("\n🎉 Database setup complete! Now run: python app.py")
