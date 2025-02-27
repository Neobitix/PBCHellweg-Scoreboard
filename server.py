from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from flask_socketio import SocketIO
from datetime import timedelta
import sqlite3
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


app = Flask(__name__)
app.secret_key = "geheimes-passwort"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365*100)  # 100 Jahre Session-Laufzeit
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

def get_db_connection():
    conn = sqlite3.connect("scores.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tisch TEXT UNIQUE,
            heim INTEGER DEFAULT 0,
            gast INTEGER DEFAULT 0,
            spielmodus TEXT DEFAULT '8-Ball'
        )
    """)
    for tisch in ["tisch1", "tisch2", "tisch3", "tisch4"]:
        c.execute("INSERT OR IGNORE INTO scores (tisch) VALUES (?)", (tisch,))
    conn.commit()
    conn.close()
init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        session["user"] = "admin"
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/scoreboard/<tisch>")
def scoreboard(tisch):
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("pbc_scoreboard.html", tisch=tisch)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@socketio.on("update_score")
def update_score(data):
    tisch, team, value = data["tisch"], data["team"], data["value"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(f"UPDATE scores SET {team} = {team} + ? WHERE tisch = ?", (value, tisch))
    conn.commit()
    scores = {row["tisch"] + "_" + key: row[key] for row in c.execute("SELECT * FROM scores") for key in ["heim", "gast"]}
    socketio.emit("update_scores", scores)
    conn.close()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
