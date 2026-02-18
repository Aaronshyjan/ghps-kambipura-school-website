from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv
import os
import threading

# ================== LOAD ENV ==================
load_dotenv()

app = Flask(__name__)

# Enable global CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# ================== GROQ ==================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================== MONGODB ==================
enquiries = None

try:
    client = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=5000
    )

    client.server_info()
    db = client["schoolDB"]
    enquiries = db["enquiries"]

    print("MongoDB Connected ✅")

except Exception as e:
    print("MongoDB Connection Failed ❌", e)

# ================== MAIL ==================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# ================== HOME ==================
@app.route('/')
def home():
    return "Backend Running ✅"

# ================== BACKGROUND EMAIL ==================
def send_email_async(parent, student, phone, class_interest, message):
    try:
        with app.app_context():
            msg = Message(
                subject="New Admission Enquiry",
                sender=app.config['MAIL_USERNAME'],
                recipients=[os.getenv("MAIL_USERNAME")]
            )

            msg.body = f"""
New Enquiry Received

Parent: {parent}
Student: {student}
Phone: {phone}
Class: {class_interest}
Message: {message}
"""
            mail.send(msg)
            print("Email Sent ✅")

    except Exception as e:
        print("Email Failed ❌", e)

# ================== ENQUIRY ==================
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    try:
        data = request.json

        parent = data.get('parent_name')
        student = data.get('student_name')
        phone = data.get('phone')
        class_interest = data.get('class_interest')
        message = data.get('message')

        # Save to MongoDB
        if enquiries is not None:
            enquiries.insert_one({
                "parent": parent,
                "student": student,
                "phone": phone,
                "class_interest": class_interest,
                "message": message
            })

        # Send email in background (SAFE)
        threading.Thread(
            target=send_email_async,
            args=(parent, student, phone, class_interest, message)
        ).start()

        return jsonify({"status": "success"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"})

# ================== CHATBOT ==================
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get("message")

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a helpful AI assistant for Government Higher Primary School, Kambipura.
Answer only about admissions, facilities, timings, teachers, location, schemes.
Keep answers short and polite.
"""
                },
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("Chat Error:", e)
        return jsonify({"reply": "AI not available right now."})

# ================== RUN ==================
if __name__ == "__main__":
    app.run()
