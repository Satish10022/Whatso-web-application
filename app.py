from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pywhatkit
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                phone TEXT,
                message TEXT,
                status TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username already exists!"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        phone = request.form['phone']
        message = request.form['message']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)
            status = "Sent"
        except Exception as e:
            status = f"Failed: {str(e)}"

        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO messages (user, phone, message, status, timestamp) VALUES (?, ?, ?, ?, ?)',
                      (session['username'], phone, message, status, timestamp))
            conn.commit()

    return render_template('dashboard.html', username=session['username'])

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('SELECT phone, message, status, timestamp FROM messages WHERE user = ? ORDER BY id DESC',
                  (session['username'],))
        messages = c.fetchall()
    return render_template('history.html', messages=messages)

if __name__ == "__main__":
    init_db()
    print("🚀 Flask app is starting...")
    app.run(debug=True)
