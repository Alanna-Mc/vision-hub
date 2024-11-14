from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
db_location = "var/visionHub.db"
app.secret_key = "temp_secret_key"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(db_location)
        g.db.row_factory = sqlite3.Row # Access columns by names rather than index
        g.db.execute("PRAGMA foreign_keys = ON;") # Enable foreign keys
    return g.db

@app.teardown_appcontext
def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("""
            SELECT u.*, r.roleName
            FROM users u
            JOIN roles r ON u.roleId = r.roleId
            WHERE u.email = ? AND u.passwordHash = ?
        """, (email, password)).fetchone()

        if user:
            return redirect(url_for("dashboard", user_id=user["userId"]))
        else:
            error ="Invalid email or password"
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):
    db = get_db()
    user =db.execute('''
        SELECT u.*, r.roleName
        FROM users u
        JOIN roles r ON u.roleId = r.roleId
        WHERE u.userId = ?
    ''', (user_id,)).fetchone()

    if user:
        return render_template("dashboard.html", user=user)
    else:
        return redirect(url_for("login"))

#@app.route("/logout")
#def logout():
   # session.clear()
   # return redirect(url_for("/"))

if __name__ == "__main__":
   app.run(debug=True, host="0.0.0.0", port=8000)
