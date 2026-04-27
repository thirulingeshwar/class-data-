import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient

# ==================================================
# FLASK APP
# ==================================================
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# ==================================================
# MONGODB CONNECTION
# ==================================================
MONGO_URI = "mongodb+srv://thirulingeshwart_db_user:NYzO4OoXyz23gSiI@cluster0.vgmryb8.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
client.admin.command("ping")   # test connection

db = client.attendance_db
students_col = db.students
attendance_col = db.records

print("MongoDB Connected Successfully 🚀")

# ==================================================
# FRONTEND ROUTE (serves index.html)
# Put your index.html inside folder: static/index.html
# ==================================================
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

# ==================================================
# STUDENT API
# ==================================================
@app.route("/api/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        data = request.json

        student = {
            "id": str(uuid.uuid4())[:8],
            "name": data.get("name", ""),
            "class": data.get("class", ""),
            "phone": data.get("phone", ""),
            "created_at": datetime.now()
        }

        students_col.insert_one(student)
        return jsonify({"message": "Student added"}), 201

    all_students = list(students_col.find({}, {"_id": 0}))
    return jsonify(all_students)


@app.route("/api/students/<student_id>", methods=["PUT", "DELETE"])
def student_actions(student_id):
    if request.method == "PUT":
        data = request.json
        students_col.update_one(
            {"id": student_id},
            {"$set": data}
        )
        return jsonify({"message": "Student updated"})

    if request.method == "DELETE":
        students_col.delete_one({"id": student_id})
        attendance_col.delete_many({"studentId": student_id})
        return jsonify({"message": "Student deleted"})


# ==================================================
# ATTENDANCE API
# ==================================================
@app.route("/api/attendance", methods=["GET", "POST"])
def attendance():
    if request.method == "POST":
        data = request.json
        records = data.get("attendance", [])
        now = datetime.now()

        for item in records:
            record = {
                "studentId": item["studentId"],
                "studentName": item["studentName"],
                "class": item["class"],
                "status": item["status"],
                "branch": data.get("branch", ""),
                "days": data.get("days", []),
                "time": now.strftime("%H:%M:%S")
            }

            attendance_col.update_one(
                {
                    "studentId": item["studentId"],
                    "date": record["date"]
                },
                {"$set": record},
                upsert=True
            )

        return jsonify({"message": "Attendance saved"}), 201

    all_records = list(attendance_col.find({}, {"_id": 0}))
    return jsonify(all_records)


# ==================================================
# DASHBOARD STATS API
# ==================================================
@app.route("/api/stats", methods=["GET"])
def stats():
    today = datetime.now().strftime("%Y-%m-%d")

    total_students = students_col.count_documents({})
    today_records = list(attendance_col.find({"date": today}))
    total_records = attendance_col.count_documents({})
    total_present = attendance_col.count_documents({"status": "Present"})

    return jsonify({
        "totalStudents": total_students,
        "todayTotal": len(today_records),
        "todayPresent": len([r for r in today_records if r["status"] == "Present"]),
        "totalRecords": total_records,
        "totalPresent": total_present
    })


# ==================================================
# EXPORT API
# ==================================================
@app.route("/api/export", methods=["GET"])
def export():
    data = list(attendance_col.find({}, {"_id": 0}))
    return jsonify(data)


# ==================================================
# RUN SERVER
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
    app = Flask(__name__)
