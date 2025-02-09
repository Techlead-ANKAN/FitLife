from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "pkt2004"  # Change this to a secure secret key

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Send OTP via email
def send_otp_email(receiver_email, otp):
    sender_email = "pradiptatalukdar2@gmail.com"  # Replace with your email
    sender_password = "vfkw nqoz uliy jxgp"  # Replace with your Gmail app password

    message = MIMEText(f"Your OTP for signup is: {otp}")
    message['Subject'] = "Signup OTP"
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Routes
@app.route('/')
def index():
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        gender = request.form['gender']
        date_of_birth = request.form['date_of_birth']
        contact_number = request.form['contact_number']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        session['otp'] = otp
        session['user_data'] = {
            'full_name': full_name,
            'gender': gender,
            'date_of_birth': date_of_birth,
            'contact_number': contact_number,
            'email': email,
            'password': password
        }

        # Send OTP to email
        if send_otp_email(email, otp):
            flash("OTP sent to your email. Please check your inbox.", "success")
            return redirect(url_for('verify_otp'))
        else:
            flash("Failed to send OTP. Please try again.", "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        return redirect(url_for('signup'))

    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session['otp']:
            # Save user data to database
            user_data = session['user_data']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (full_name, gender, date_of_birth, contact_number, email, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_data['full_name'],
                user_data['gender'],
                user_data['date_of_birth'],
                user_data['contact_number'],
                user_data['email'],
                user_data['password']
            ))
            conn.commit()
            conn.close()

            # Clear session data
            session.pop('otp', None)
            session.pop('user_data', None)

            flash("Signup successful! Please sign in.", "success")
            return redirect(url_for('signin'))
        else:
            flash("Invalid OTP. Please try again.", "error")
            return redirect(url_for('verify_otp'))

    return render_template('verify_otp.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            flash("Signin successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('signin'))

    return render_template('signin.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        flash("User not found.", "error")
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('signin'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)