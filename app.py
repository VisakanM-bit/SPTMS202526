from flask import Flask, request, render_template, redirect, url_for, session
import smtplib
import secrets
import time
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = "supersecretkey"
@app.route('/')
def home():
    return redirect(url_for('login'))
tokens = {}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        token = secrets.token_urlsafe(16)
        expiry = time.time() + 600  
        tokens[token] = {'email': email, 'expiry': expiry}
        link = f"http://127.0.0.1:5000/verify/{token}"
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
    message = f"Subject: Your Bus Tracking Login Link\n\nClick to log in: {link}"
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)
if __name__ == '__main__':
    app.run(debug=True)
