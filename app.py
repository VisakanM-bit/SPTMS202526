from flask import Flask, request, render_template, redirect, url_for, session
import smtplib
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")

# Replace with your Render domain
# For local testing
BASE_URL = "https://sptms202526.onrender.com/"


# Serializer for token generation
serializer = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        # Generate token with email, valid for 10 minutes (600 seconds)
        token = serializer.dumps(email, salt='email-login')
        link = f"{BASE_URL}/verify/{token}"
        send_email(email, link)
        return render_template("login.html", message="Check your email for the login link!")
    return render_template("login.html")

@app.route('/verify/<token>')
def verify(token):
    try:
        # Max age 600 seconds = 10 minutes
        email = serializer.loads(token, salt='email-login', max_age=600)
        session['user'] = email
        return redirect(url_for('dashboard'))
    except SignatureExpired:
        return "Token expired!"
    except BadSignature:
        return "Invalid token!"

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("page2.html", user=session['user'])
    else:
        return redirect(url_for('login'))

def send_email(to_email, link):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    message = f"Subject: Your Bus Tracking Login Link\n\nClick to log in: {link}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
