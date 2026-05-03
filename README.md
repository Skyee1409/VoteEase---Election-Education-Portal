# 🗳️ VoteEase — Election Education Portal

VoteEase is a modern, responsive web application designed to educate and assist voters. It provides essential information about voter registration, eligibility, polling booths, and election schedules, featuring a built-in AI chatbot and multi-language support.

## ✨ Features

- **🤖 VoteBot (AI Chatbot):** Instant answers to common voter queries (registration, documents, eligibility).
- **📍 Polling Booth Locator:** Find your nearest voting center by city or pincode.
- **📅 Election Timeline:** Track upcoming National, State, and Local elections.
- **🌍 Multi-language Support:** Toggle between English and Hindi.
- **🎙️ Voice Assistance:** Built-in text-to-speech for better accessibility.
- **📱 Responsive Design:** Premium, glassmorphism-inspired UI that works on all devices.
- **🔔 Notifications:** Subscribe for election alerts via Email or SMS.

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite (for local storage)
- **Frontend:** HTML5, Vanilla CSS3, Javascript (ES6+)
- **Environment:** `python-dotenv` for configuration

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/YOUR_USERNAME/VoteEase.git
cd VoteEase
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (use `.env.example` as a template):
```env
SECRET_KEY=your-secret-key
```

### 4. Run the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## 📁 Project Structure

- `app.py`: Main Flask application and API endpoints.
- `templates/`: HTML templates.
- `static/`: CSS styles, client-side JS, and assets.
- `voteease.db`: SQLite database file (auto-generated).
- `.env`: Sensitive configuration (ignored by Git).

## 🛡️ Security Note
The `.env` file and `voteease.db` are excluded from Git to prevent leaking sensitive information and local data. Always use environment variables for secrets.

---
Built with ❤️ for Voter Awareness.
