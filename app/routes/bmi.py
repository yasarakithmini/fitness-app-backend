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


@bmi_bp.route('/api/fitness/last-two-records', methods=['GET'])
def get_last_two_records():
    user_id = request.args.get('user_id')  # Get user ID from query parameters

    # Query the last two records for the user
    records = UserFitnessRecord.query.filter_by(user_id=user_id).order_by(UserFitnessRecord.date.desc()).limit(2).all()

    if len(records) < 2:
        return jsonify({'message': 'Not enough records to compare'}), 400

    # Extract relevant data from the records
    record_1 = {
        'age': records[0].age,
        'gender': records[0].gender,
        'height': records[0].height,
        'weight': records[0].weight,
        'bmi': records[0].bmi,
        'waist': records[0].waist,
        'hip': records[0].hip,
        'whr': records[0].whr
    }

    record_2 = {
        'age': records[1].age,
        'gender': records[1].gender,
        'height': records[1].height,
        'weight': records[1].weight,
        'bmi': records[1].bmi,
        'waist': records[1].waist,
        'hip': records[1].hip,
        'whr': records[1].whr
    }

    return jsonify({
        'record_1': record_1,
        'record_2': record_2
    })
