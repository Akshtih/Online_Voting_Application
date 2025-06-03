# Online Voting Portal

A Flask-based application for online community voting and feedback collection with secure submission and real-time results.

## Technologies

- **Backend**: Flask, Python 3.9+
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF
- **Real-time Updates**: Flask-SocketIO
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js
- **Date Handling**: Flatpickr.js

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/akshtih/online_voting_application.git
cd online_voting_portal
```

2. **Setup virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf flask-migrate python-dotenv email-validator flask-bcrypt flask-socketio
```

4. **Configure environment**
```bash
# Create .env file with:
SECRET_KEY=your_secret_key_here
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///voting_portal.db
```

5. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Create admin user**
```bash
python create_admin.py
```

7. **Run the application**
```bash
python run.py
```

8. **Access the application**
   - URL: http://127.0.0.1:5000/
   - Admin login:
     - Email: admin@example.com
     - Password: adminpassword

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Online Voting Portal"
git remote add origin https://github.com/akshtih/online_voting_application.git
git push -u origin main
```
