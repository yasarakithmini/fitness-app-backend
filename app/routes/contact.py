# app/routes/contact.py
from flask import Blueprint, request, jsonify
import smtplib
from email.message import EmailMessage
import os

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    sender_email = data.get('email')
    message_content = data.get('message')

    try:
        # Email setup
        msg = EmailMessage()
        msg['Subject'] = 'New Contact Us Message'
        msg['From'] = sender_email
        msg['To'] = 'yasarakithmini9@gmail.com'
        msg.set_content(f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_content}")

        # Use Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"error": "Failed to send email"}), 500
