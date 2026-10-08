import mysql.connector
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "py_doctor_appoinment_booking",
    "charset": "utf8",
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/doctor_register", methods=["GET", "POST"])
def doctor_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        doctor_name = request.form["doctor_name"]
        speciality = request.form["speciality"]
        experience = request.form["experience"]

        doctor_image = request.files.get("doctor_image")
        if not doctor_image or not allowed_file(doctor_image.filename):
            flash("Invalid image file. Please upload a valid image.", "error")
            return redirect(url_for("doctor_register"))

        filename = secure_filename(doctor_image.filename)
        doctor_image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        doctor_image.save(doctor_image_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctor_tb WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Username already exists.", "error")
            return redirect(url_for("doctor_register"))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            """INSERT INTO doctor_tb
            (username, password, email, doctor_name, speciality, doctor_image, experience)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (username, hashed_password, email, doctor_name, speciality, doctor_image_path, experience),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return render_template("doctor_login.html", alert_message="Registration successful! Please log in.")

    return render_template("doctor_register.html")

@app.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctor_tb WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["doc_name"] = username
            return redirect(url_for("doctor_index"))
        flash("Invalid credentials. Please try again.")
    return render_template("doctor_login.html")

@app.route("/patient_register", methods=["GET", "POST"])
def patient_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        gender = request.form["gender"]
        age = request.form["age"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient_tb WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Username already exists.", "error")
            return redirect(url_for("patient_register"))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            """INSERT INTO patient_tb (username, password, email, mobile, gender, age)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (username, hashed_password, email, mobile, gender, age),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return render_template("patient_login.html", alert_message="Registration successful! Please log in.")

    return render_template("patient_register.html")

@app.route("/patient_login", methods=["GET", "POST"])
def patient_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient_tb WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_name"] = username
            return redirect(url_for("patient_index"))
        flash("Invalid credentials. Please try again.")
    return render_template("patient_login.html")

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.root_path, "uploads"), filename)

@app.route("/appointment/<string:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    if "user_name" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("patient_login"))

    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO appointments
            (user_name, doctor_id, appointment_date, appointment_time, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                session["user_name"],
                doctor_id,
                request.form["appointment_date"],
                request.form["appointment_time"],
                request.form["description"],
                "Pending",
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("patient_index"))

    return render_template("appointment.html", doctor_id=doctor_id)

@app.route("/patient_index")
def patient_index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctor_tb")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("patient_index.html", doctors=doctors)

@app.route("/doctor/<int:doctor_id>")
def view_doctor(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctor_tb WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("doctor_detail.html", doctor=doctor)

@app.route("/all_appointments")
def show_all_appointments():
    if "user_name" not in session:
        return redirect(url_for("patient_login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM appointments WHERE user_name = %s ORDER BY created_at DESC",
        (session["user_name"],),
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("all_appointments.html", appointments=appointments)

@app.route("/pending_appointment")
def show_pending_appointments():
    if "user_name" not in session:
        return redirect(url_for("patient_login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM appointments WHERE user_name = %s AND status = 'Pending' ORDER BY created_at DESC",
        (session["user_name"],),
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("pending_appointments.html", appointments=appointments)

@app.route("/accepted_appointment")
def show_accepted_appointments():
    if "user_name" not in session:
        return redirect(url_for("patient_login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM appointments WHERE user_name = %s AND status = 'accepted' ORDER BY created_at DESC",
        (session["user_name"],),
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("accepted_appointments.html", appointments=appointments)

@app.route("/doc_accepted_appointment")
def doc_accepted_appointments():
    if "doc_name" not in session:
        return redirect(url_for("doctor_login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM appointments WHERE doctor_id = %s AND status = 'accepted' ORDER BY created_at DESC",
        (session["doc_name"],),
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("doc_accepted_appointments.html", appointments=appointments)

@app.route("/doctor_index", methods=["GET", "POST"])
def doctor_index():
    if "doc_name" not in session:
        return redirect(url_for("doctor_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        appointment_id = request.form["appointment_id"]
        action = request.form["action"]
        new_status = "accepted" if action == "accept" else "Rejected"
        cursor.execute(
            "UPDATE appointments SET status = %s WHERE id = %s",
            (new_status, appointment_id),
        )
        conn.commit()

    cursor.execute(
        """SELECT * FROM appointments
        WHERE doctor_id = %s AND status = 'Pending'
        ORDER BY created_at DESC""",
        (session["doc_name"],),
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("doctor_index.html", appointments=appointments)

if __name__ == "__main__":
    app.run(debug=True)
