from flask import Flask, render_template, redirect, url_for, request, flash, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Logic for user login
        username = request.form['username']
        password = request.form['password']
        # Validate credentials (this is just a placeholder)
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Logic for user registration
        username = request.form['username']
        password = request.form['password']
        # Save user to database (this is just a placeholder)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard/index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)