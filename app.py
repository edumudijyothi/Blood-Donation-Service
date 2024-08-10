from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email_address']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['email_address'] = email
            return redirect(url_for('index'))
        else:
            flash('Invalid email_address or password')
    
    return render_template('login.html')

@app.route('/registeration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email_address']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email_address, password) VALUES (?, ?)', (email_address, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Email already exists')
            conn.close()
            return redirect(url_for('registeration'))
        conn.close()
        flash('Registration successful, please log in.')
        return redirect(url_for('login'))

    return render_template('registeration.html')

@app.route('/logout')
def logout():
    session.pop('email_address', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
