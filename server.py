from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import os

app = Flask(__name__)

# Flask-Session Konfiguration für langfristige Sessions (10 Jahre)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 10 * 365 * 24 * 60 * 60  # 10 Jahre
Session(app)

# Verfügbare Spielmodi
AVAILABLE_MODES = ["8-Ball", "9-Ball", "Straight Pool", "One Pocket", "Rotation"]

@app.route('/')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "deinPasswort":  # Passwort anpassen
            session['logged_in'] = True
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/update_mode', methods=['POST'])
def update_mode():
    data = request.get_json()
    selected_mode = data.get('mode')
    if selected_mode in AVAILABLE_MODES:
        session['game_mode'] = selected_mode
        return jsonify({'success': True, 'mode': selected_mode})
    return jsonify({'success': False, 'error': 'Invalid mode'}), 400

@app.route('/get_mode', methods=['GET'])
def get_mode():
    return jsonify({'mode': session.get('game_mode', '8-Ball')})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')