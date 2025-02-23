import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO

# Flask App Setup
app = Flask(__name__, static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = "super_secure_password_key"  # Change this for security!

# Passwort für den Login
PASSWORD = "billard2024"  # Hier kannst du das Passwort ändern!

# Löscht die Datenbank bei jedem Neustart des Servers
if os.path.exists("scores.db"):
    os.remove("scores.db")

# Initialisiere die Datenbank mit Heim- und Gäste-Score für jeden Tisch
def init_db():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (tisch TEXT, team TEXT, score INTEGER, PRIMARY KEY (tisch, team))''')
    for i in range(1, 5):
        c.execute("INSERT OR IGNORE INTO scores (tisch, team, score) VALUES (?, 'heim', 0)", (f"tisch{i}",))
        c.execute("INSERT OR IGNORE INTO scores (tisch, team, score) VALUES (?, 'gaste', 0)", (f"tisch{i}",))
    conn.commit()
    conn.close()

init_db()

# Hole Punktestände
def get_scores():
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("SELECT tisch, team, score FROM scores")
    scores = {}
    for tisch, team, score in c.fetchall():
        scores[f"{tisch}_{team}"] = score
    conn.close()
    return scores

# Startseite mit Passwortabfrage
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("index.html", error="Falsches Passwort!")
    return render_template("index.html")

# Dashboard mit Auswahl zwischen den Anzeigen
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# Route für Tischbildschirm
@app.route("/tisch<int:tisch_num>")
def tisch(tisch_num):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("pbc_scoreboard.html", tisch=f"tisch{tisch_num}")

# Route für Gemeinschaftsbildschirm
@app.route("/overview")
def gemeinschaftsbildschirm():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("gemeinschaft.html", scores=get_scores())

# Update Punktestand
@app.route("/update_score", methods=["POST"])
def update_score():
    if not session.get("logged_in"):
        return jsonify(success=False, error="Nicht eingeloggt"), 403
    data = request.json
    tisch = data.get("tisch")
    team = data.get("team")
    change = int(data.get("change", 0))

    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("UPDATE scores SET score = score + ? WHERE tisch = ? AND team = ?", (change, tisch, team))
    conn.commit()
    conn.close()

    scores = get_scores()
    socketio.emit("update_scores", scores)
    return jsonify(success=True, scores=scores)

# Reset alle Punkte
@app.route("/reset_scores", methods=["POST"])
def reset_scores():
    if not session.get("logged_in"):
        return jsonify(success=False, error="Nicht eingeloggt"), 403
    conn = sqlite3.connect("scores.db")
    c = conn.cursor()
    c.execute("UPDATE scores SET score = 0")
    conn.commit()
    conn.close()
    
    scores = get_scores()
    socketio.emit("update_scores", scores)
    return jsonify(success=True, scores=scores)

# WebSocket Verbindung
@socketio.on("connect")
def connect():
    socketio.emit("update_scores", get_scores())

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
