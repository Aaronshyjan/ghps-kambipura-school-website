from flask import Flask, request, jsonify, make_response
from flask_mail import Mail, Message
from flask_cors import CORS
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# ================== GROQ ==================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================== MONGODB ==================
enquiries = None

try:
    client = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=5000
    )

    client.server_info()  # test connection

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

# ================== ENQUIRY ==================
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    try:
        parent = request.form.get('parent_name')
        student = request.form.get('student_name')
        phone = request.form.get('phone')
        class_interest = request.form.get('class_interest')
        message = request.form.get('message')

        # Save to DB
        if enquiries is not None:
            enquiries.insert_one({
                "parent": parent,
                "student": student,
                "phone": phone,
                "class_interest": class_interest,
                "message": message
            })

        # Send Email
        msg = Message(
            subject="New Admission Enquiry",
            sender=app.config['MAIL_USERNAME'],
            recipients=["noelsabu25@gmail.com"]
        )

        msg.body = f"""
New Enquiry Received

Parent: {parent}
Student: {student}
Phone: {phone}
Class: {class_interest}
Message: {message}
"""

        try:
            mail.send(msg)
            print("Email Sent ✅")
        except Exception as e:
            print("Email Failed ❌", e)

        return "success"

    except Exception as e:
        print("Error:", e)
        return "error"

# ================== CHATBOT ==================
@app.route('/chat', methods=['POST','OPTIONS'])
def chat():

    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

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

        res = jsonify({"reply": reply})
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res

    except Exception as e:
        print("Chat Error:", e)
        res = jsonify({"reply": "AI not available right now."})
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res

# ================== RUN ==================
if __name__ == "__main__":
   app.run(debug=True, host="0.0.0.0", port=5000)
