from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv
import resend
import os

# ================== LOAD ENV ==================
load_dotenv()

app = Flask(__name__)
CORS(app)

# ================== GROQ ==================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================== RESEND ==================
resend.api_key = os.getenv("RESEND_API_KEY")

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

# ================== HOME ==================
@app.route('/')
def home():
    return "Backend Running ✅"

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

        # Send Email via Resend
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["noelsabu25@gmail.com"],
            "subject": "New Admission Enquiry",
            "html": f"""
                <h3>New Enquiry Received</h3>
                <p><b>Parent:</b> {parent}</p>
                <p><b>Student:</b> {student}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Class:</b> {class_interest}</p>
                <p><b>Message:</b> {message}</p>
            """
        })

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
