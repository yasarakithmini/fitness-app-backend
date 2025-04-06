from flask import Blueprint, request, jsonify
from app import mysql
import uuid

bmi_bp = Blueprint('bmi', __name__)

def calculate_bmi(weight, height):
    """Calculate BMI (height in cm)"""
    height_m = float(height) / 100  # Convert height from cm to meters
    return round(float(weight) / (height_m ** 2), 2)

def calculate_whr(waist, hip):
    """Calculate Waist-to-Hip Ratio"""
    return round(float(waist) / float(hip), 2)

@bmi_bp.route('/fitness/save', methods=['POST'])
def save_fitness_record():
    """Save BMI, Waist-Hip Ratio, and other fitness metrics"""
    data = request.json
    user_id = data.get('user_id')
    age = data.get('age')
    gender = data.get('gender')
    height = data.get('height')
    weight = data.get('weight')
    waist = data.get('waist')
    hip = data.get('hip')

    if not all([user_id, age, gender, height, weight, waist, hip]):
        return jsonify({"message": "All fields are required"}), 400

    bmi = calculate_bmi(weight, height)
    whr = calculate_whr(waist, hip)

    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO user_fitness_records
            (id, user_id, age, gender, height, weight, bmi, waist, hip, whr, record_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ''', (str(uuid.uuid4()), user_id, age, gender, height, weight, bmi, waist, hip, whr))
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "Fitness record saved successfully",
            "bmi": bmi,
            "whr": whr
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bmi_bp.route('/fitness/latest/<user_id>', methods=['GET'])
def get_latest_fitness_records(user_id):
    """Fetch the two most recent fitness records of the user"""
    try:
        print(f"Received user_id: {user_id}")  # This will print the user_id in your terminal/console

        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT age, gender, height, weight, bmi, waist, hip, whr, record_date
            FROM user_fitness_records
            WHERE user_id = %s
            ORDER BY record_date DESC
            LIMIT 2
        ''', (user_id,))

        records = cursor.fetchall()
        cursor.close()

        if not records:
            print("No records found for this user_id")  # Log message for debugging
            return jsonify({"message": "No records found"}), 404

        result = []
        for record in records:
            result.append({
                "age": record[0],
                "gender": record[1],
                "height": record[2],
                "weight": record[3],
                "bmi": record[4],
                "waist": record[5],
                "hip": record[6],
                "whr": record[7],
                "record_date": record[8].strftime("%Y-%m-%d %H:%M:%S")
            })

        print("Fetched Records:", result)
        return jsonify(result), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error if any exception occurs
        return jsonify({"error": str(e)}), 500
