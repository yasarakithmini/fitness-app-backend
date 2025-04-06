import os
from flask import Blueprint, request, jsonify
import smtplib
from email.message import EmailMessage

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name')
    sender_email = data.get('email')
    message_content = data.get('message')

    # Debug print environment variable values
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    print("EMAIL_USER:", email_user)
    print("EMAIL_PASS is set:", email_pass is not None)

    if not email_user or not email_pass:
        return jsonify({"error": "Email credentials not set in environment variables"}), 500

    try:
        msg = EmailMessage()
        msg['Subject'] = 'New Contact Us Message'
        msg['From'] = sender_email
        msg['To'] = 'fixfit1111@gmail.com'
        msg.set_content(f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_content}")

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return jsonify({"error": "Failed to send email"}), 500
