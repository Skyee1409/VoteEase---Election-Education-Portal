from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import json
import random
import string
from datetime import datetime, timedelta
import os
from functools import wraps

load_dotenv()  # reads .env file

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'voteease-secret-key-2024')
CORS(app)

# ─── Database Configuration (SQLite — no setup needed!) ───────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'voteease.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

def init_db():
    """Auto-creates tables on first run."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            aadhaar TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            phone TEXT,
            subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(email, phone)
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database ready: voteease.db")

# ─── AI Chatbot Responses ─────────────────────────────────────────────────────
CHATBOT_RESPONSES = {
    "register": {
        "keywords": ["register", "registration", "sign up", "enroll", "how to register"],
        "response": "📋 To register as a voter:\n1. Visit your nearest Election Commission office or register online\n2. Provide your Aadhaar card / National ID\n3. Fill Form 6 (new voter) or Form 8 (address change)\n4. Submit with photo proof\n5. You'll receive SMS confirmation within 7-10 days."
    },
    "eligibility": {
        "keywords": ["eligible", "eligibility", "who can vote", "age", "qualify"],
        "response": "✅ Voter Eligibility Requirements:\n• Must be a citizen of India\n• Must be 18 years of age or older\n• Must be ordinarily resident in the constituency\n• Must not be of unsound mind\n• Must not be disqualified under any law"
    },
    "documents": {
        "keywords": ["document", "id proof", "id card", "photo id", "papers"],
        "response": "📄 Accepted Voter ID Documents:\n• Voter ID Card (EPIC)\n• Aadhaar Card\n• Passport\n• Driving License\n• PAN Card with photo\n• Government employee ID\n• Bank/Post Office passbook with photo"
    },
    "polling": {
        "keywords": ["polling", "booth", "where", "voting center", "station", "location"],
        "response": "📍 To find your polling booth:\n1. Use the 'Polling Booth Locator' on this portal\n2. Enter your voter ID or Aadhaar number\n3. Or SMS 'BOOTH [Voter ID]' to 1950\n4. Visit voterportal.eci.gov.in\nPolling booths open from 7 AM to 6 PM on election day."
    },
    "date": {
        "keywords": ["date", "when", "election date", "voting date", "schedule"],
        "response": "📅 Upcoming Elections 2024-2025:\n• General Elections: Refer to Election Commission notifications\n• Check the Election Timeline section on this portal\n• Subscribe to SMS alerts to get date notifications\n• Visit eci.gov.in for official schedule"
    },
    "lost_card": {
        "keywords": ["lost", "missing", "duplicate", "card lost", "damaged"],
        "response": "🔄 Lost/Damaged Voter ID Card:\n1. File an FIR at local police station\n2. Visit election office with FIR copy + photos\n3. Fill Form EPIC (duplicate request)\n4. Or apply online at nvsp.in\n5. New card delivered within 30-45 days"
    },
    "correction": {
        "keywords": ["correction", "wrong", "mistake", "update", "change name", "change address"],
        "response": "✏️ Voter ID Corrections:\n• Name correction: Fill Form 8A\n• Address change (same constituency): Form 8A\n• Address change (new constituency): Form 6 + Form 7\n• Apply online at nvsp.in or at election office\n• Corrections take 15-30 days to process"
    },
    "nri": {
        "keywords": ["nri", "abroad", "overseas", "foreign", "outside india"],
        "response": "🌍 NRI Voter Registration:\n• NRIs can register in their home constituency\n• Fill Form 6A on the NVSP portal\n• Submit Indian passport copy\n• Must be physically present to vote (no postal voting yet)\n• Visit eci.gov.in/nri-voters for details"
    },
    "help": {
        "keywords": ["help", "hi", "hello", "hey", "start", "assist", "support"],
        "response": "👋 Hello! I'm VoteBot, your voter assistance AI!\n\nI can help you with:\n• 📋 Voter Registration\n• ✅ Eligibility Criteria\n• 📄 Required Documents\n• 📍 Polling Booth Location\n• 📅 Election Dates\n• 🔄 Lost/Damaged Card\n• ✏️ Voter ID Corrections\n• 🌍 NRI Voting\n\nJust type your question!"
    }
}

def get_chatbot_response(message):
    message_lower = message.lower()
    for category, data in CHATBOT_RESPONSES.items():
        for keyword in data['keywords']:
            if keyword in message_lower:
                return data['response']
    return ("🤔 I'm not sure about that specific query.\n\n"
            "You can ask me about:\n• Voter Registration\n• Eligibility\n• Documents needed\n"
            "• Polling Booth location\n• Election Dates\n• Lost Voter ID\n• Corrections\n\n"
            "Or call the helpline: 📞 1950")

# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    response = get_chatbot_response(message)
    return jsonify({
        'response': response,
        'timestamp': datetime.now().strftime('%H:%M')
    })

@app.route('/api/find-booth', methods=['POST'])
def find_booth():
    data = request.get_json()
    pincode = data.get('pincode', '')
    city = data.get('city', '')

    # Sample polling booths data
    sample_booths = [
        {
            'name': 'Government Senior Secondary School',
            'address': f'Ward 5, Near Main Market, {city or "Your City"}',
            'distance': '0.8 km',
            'timing': '7:00 AM - 6:00 PM',
            'booth_number': 'B-001',
            'facilities': ['Wheelchair Access', 'Drinking Water', 'Shade']
        },
        {
            'name': 'Community Hall, Sector 12',
            'address': f'Block C, Sector 12, {city or "Your City"}',
            'distance': '1.2 km',
            'timing': '7:00 AM - 6:00 PM',
            'booth_number': 'B-002',
            'facilities': ['Wheelchair Access', 'Parking', 'First Aid']
        },
        {
            'name': 'Municipal Corporation Office',
            'address': f'Main Road, {city or "Your City"} - {pincode}',
            'distance': '2.1 km',
            'timing': '7:00 AM - 6:00 PM',
            'booth_number': 'B-003',
            'facilities': ['AC Hall', 'Parking', 'Drinking Water']
        }
    ]
    return jsonify({'booths': sample_booths, 'total': len(sample_booths)})

@app.route('/api/subscribe-notifications', methods=['POST'])
def subscribe_notifications():
    data = request.get_json()
    email = data.get('email', '')
    phone = data.get('phone', '')
    if not email and not phone:
        return jsonify({'error': 'Email or phone required'}), 400

    db = get_db()
    try:
        db.execute("""
            INSERT OR REPLACE INTO notifications (email, phone)
            VALUES (?, ?)
        """, (email, phone))
        db.commit()
    except Exception as e:
        print(f"DB error: {e}")
    finally:
        db.close()

    return jsonify({'success': True, 'message': 'Subscribed successfully! You will receive election notifications.'})

@app.route('/api/elections', methods=['GET'])
def get_elections():
    elections = [
        {
            'id': 1,
            'title': 'General Elections 2024',
            'type': 'National',
            'date': '2024-04-19',
            'phases': 7,
            'status': 'completed',
            'description': 'Indian General Elections - 18th Lok Sabha'
        },
        {
            'id': 2,
            'title': 'Maharashtra State Elections',
            'type': 'State',
            'date': '2024-11-20',
            'phases': 1,
            'status': 'completed',
            'description': 'Maharashtra Legislative Assembly Elections'
        },
        {
            'id': 3,
            'title': 'Delhi Assembly Elections',
            'type': 'State',
            'date': '2025-02-05',
            'phases': 1,
            'status': 'completed',
            'description': 'Delhi Legislative Assembly Elections 2025'
        },
        {
            'id': 4,
            'title': 'Bihar State Elections',
            'type': 'State',
            'date': '2025-10-15',
            'phases': 3,
            'status': 'upcoming',
            'description': 'Bihar Legislative Assembly Elections 2025'
        },
        {
            'id': 5,
            'title': 'Local Body Elections 2025',
            'type': 'Local',
            'date': '2025-12-01',
            'phases': 1,
            'status': 'upcoming',
            'description': 'Municipal Corporation Elections across major cities'
        }
    ]
    return jsonify({'elections': elections})

# ─── Auto-create tables on startup ───────────────────────────────────────────
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
