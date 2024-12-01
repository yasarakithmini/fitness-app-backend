from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fitness_app'

mysql = MySQL(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = str(uuid.uuid4())
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt())
    user_type = data.get('user_type', 'User')  # Default to 'User' if not provided

    cursor = mysql.connection.cursor()
    cursor.execute('''
        INSERT INTO users (id, first_name, last_name, email, password, user_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, first_name, last_name, email, password, user_type))
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'user_type': user_type,
        'message': 'User registered successfully!'
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' SELECT * FROM users WHERE email = %s ''', (email,))
    user = cursor.fetchone()
    cursor.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({
            'id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'user_type': user['user_type'],
            'message': 'User logged in successfully!'
        })
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/api/trainers', methods=['GET'])
def get_trainers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' SELECT id, first_name, last_name FROM users WHERE user_type = %s ''', ('Trainer',))
    trainers = cursor.fetchall()
    cursor.close()

    trainer_data = [{"id": trainer['id'], "name": f"{trainer['first_name']} {trainer['last_name']}"} for trainer in trainers]

    return jsonify(trainer_data)



@app.route('/api/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    user_id = data.get('id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT password FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                UPDATE users
                SET first_name = %s, last_name = %s, email = %s, password = %s
                WHERE id = %s
            ''', (first_name, last_name, email, hashed_password, user_id))
        else:
            cursor.execute('''
                UPDATE users
                SET first_name = %s, last_name = %s, email = %s
                WHERE id = %s
            ''', (first_name, last_name, email, user_id))

        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Settings updated successfully!'})
    else:
        return jsonify({'message': 'Current password is incorrect'}), 400

meetings = []

@app.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    data = request.get_json()
    user_id = data.get('user_id')
    trainer_id = data.get('trainer_id')
    date_time = data.get('date_time')

    if not all([user_id, trainer_id, date_time]):
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        INSERT INTO meetings (user_id, trainer_id, date_time, status)
        VALUES (%s, %s, %s, %s)
    ''', (user_id, trainer_id, date_time, 'Pending'))
    mysql.connection.commit()

    # Fetch the ID of the newly created meeting
    meeting_id = cursor.lastrowid
    cursor.close()

    return jsonify({
        'id': meeting_id,
        'user_id': user_id,
        'trainer_id': trainer_id,
        'datetime': date_time,
        'status': 'Pending'
    }), 201

    return jsonify(meeting_request), 201
@app.route('/api/meeting-requests/<trainer_id>', methods=['GET'])
def get_meeting_requests(trainer_id):
    try:
        # Fetch all meetings for the given trainer ID
        meetings = Meetings.query.filter_by(trainer_id=trainer_id).all()
        # Convert the meetings to a list of dictionaries
        meetings_list = [meetings.to_dict() for meeting in meetings]
        return jsonify(meetings_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    @app.route('/api/meeting-requests/<int:meeting_id>/accept', methods=['POST'])
    def accept_meeting(meeting_id):
        cursor = mysql.connection.cursor()
        cursor.execute('''
            UPDATE meetings
            SET status = %s
            WHERE id = %s
        ''', ('accepted', meeting_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'id': meeting_id, 'status': 'accepted'}), 200





        # Route to save user BMI record
        @app.route('/api/bmi/save', methods=['POST'])
        def save_bmi():
            data = request.json
            user_id = data.get('user_id')
            age = data.get('age')
            gender = data.get('gender')
            height = data.get('height')
            weight = data.get('weight')
            bmi = data.get('bmi')


            if not all([user_id, age, gender, height, weight]):
                return jsonify({"message": "All fields are required"}), 400

            bmi = calculate_bmi(weight, height)
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO user_health_records (id, user_id, age, gender, height, weight, bmi, record_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ''', (str(uuid.uuid4()), user_id, age, gender, height, weight, bmi))
            mysql.connection.commit()
            cursor.close()

            return jsonify({
                "message": "BMI record saved successfully",
                "bmi": bmi
            })
        # Route to fetch BMI comparison (current vs last month)
        @app.route('/api/bmi/compare', methods=['GET'])
        def compare_bmi():
            user_id = request.args.get('user_id')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Get this month's record
            cursor.execute('''
                SELECT bmi, record_date FROM user_health_records
                WHERE user_id = %s AND MONTH(record_date) = MONTH(NOW()) AND YEAR(record_date) = YEAR(NOW())
                ORDER BY record_date DESC LIMIT 1
            ''', (user_id,))
            this_month_record = cursor.fetchone()

            # Get last month's record
            cursor.execute('''
                SELECT bmi, record_date FROM user_health_records
                WHERE user_id = %s AND MONTH(record_date) = MONTH(NOW() - INTERVAL 1 MONTH)
                AND YEAR(record_date) = YEAR(NOW())
                ORDER BY record_date DESC LIMIT 1
            ''', (user_id,))
            last_month_record = cursor.fetchone()

            cursor.close()

            if this_month_record and last_month_record:
                return jsonify({
                    "this_month_bmi": this_month_record['bmi'],
                    "last_month_bmi": last_month_record['bmi'],
                    "this_month_date": this_month_record['record_date'],
                    "last_month_date": last_month_record['record_date'],
                    "comparison": round(this_month_record['bmi'] - last_month_record['bmi'], 2)
                })
            else:
                return jsonify({
                    "message": "No sufficient records found for comparison"
                }), 404




    if __name__ == '__main__':
        app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)