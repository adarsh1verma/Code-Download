from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, session
import os
import json
import random
import string

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join("static", "docs")
CODES_FILE = "codes.json"

USERNAME = "admin"
PASSWORD = "password123"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_codes():
    if not os.path.exists(CODES_FILE):
        return {}
    with open(CODES_FILE, "r") as f:
        return json.load(f)

def save_codes(codes):
    with open(CODES_FILE, "w") as f:
        json.dump(codes, f, indent=4)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    codes = load_codes()
    if request.method == "POST":
        code = request.form.get("code").strip()
        filename = codes.get(code)
        if filename:
            return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
        else:
            flash("Invalid code.")
            return redirect(url_for("index"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        if username == USERNAME and password == PASSWORD:
            session["admin"] = True
            flash("Logged in successfully.")
            return redirect(url_for("admin"))
        else:
            flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out.")
    return redirect(url_for("login"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        flash("Login required.")
        return redirect(url_for("login"))

    codes = load_codes()

    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename:
            filename = uploaded_file.filename
            uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))

            user_code = request.form.get("code").strip()
            code = user_code if user_code else generate_code()
            while code in codes:
                code = generate_code()

            codes[code] = filename
            save_codes(codes)
            flash(f"Uploaded successfully with code: {code}")
        else:
            flash("No file selected.")
        return redirect(url_for("admin"))

    return render_template("admin.html", codes=codes)
if __name__ == "__main__":
    app.run(debug=True)
