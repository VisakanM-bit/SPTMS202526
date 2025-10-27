from flask import Flask, request, render_template, redirect, url_for, session
import smtplib
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

tokens = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        token = secrets.token_urlsafe(16)
        expiry = time.time() + 600  # 10 minutes

        tokens[token] = {'email': email, 'expiry': expiry}

        # ✅ Use production base URL if available
        base_url = os.environ.get("BASE_URL", "https://sptms-202526-9c6k.vercel.app/")
        link = f"{base_url}/verify/{token}"

        send_email(email, link)
        return render_template("login.html", message="Check your email for the login link!")

    return render_template("login.html")


@app.route('/verify/<token>')
def verify(token):
    if token in tokens:
        data = tokens[token]
        if time.time() < data['expiry']:
            session['user'] = data['email']
            del tokens[token]
            return redirect(url_for('dashboard'))
        else:
            return "Token expired!"
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

    if not sender_email or not sender_password:
        print("❌ Missing email credentials in environment variables")
        return

    message = f"Subject: Your Bus Tracking Login Link\n\nClick to log in: {link}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message)
    except Exception as e:
        print("❌ Email sending failed:", e)


# ✅ Render-friendly run block
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
