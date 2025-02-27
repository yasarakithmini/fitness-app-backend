from flask import Blueprint, request, jsonify
from app import mysql

meetings_bp = Blueprint('meetings', __name__)


@meetings_bp.route('/api/schedule-meeting', methods=['POST'])
def schedule_meeting():
    data = request.get_json()
    user_id = data.get('user_id')
    trainer_id = data.get('trainer_id')
    date_time = data.get('date_time')

    if not all([user_id, trainer_id, date_time]):
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute('''
        INSERT INTO meetings (user_id, trainer_id, date_time, status)
        VALUES (%s, %s, %s, %s)
    ''', (user_id, trainer_id, date_time, 'Pending'))
    mysql.connection.commit()

    meeting_id = cursor.lastrowid
    cursor.close()

    return jsonify({
        'id': meeting_id,
        'user_id': user_id,
        'trainer_id': trainer_id,
        'datetime': date_time,
        'status': 'Pending'
    }), 201


@meetings_bp.route('/api/meeting-requests/<trainer_id>', methods=['GET'])
def get_meeting_requests(trainer_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT * FROM meetings WHERE trainer_id = %s
        ''', (trainer_id,))
        meetings = cursor.fetchall()
        cursor.close()

        return jsonify(meetings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@meetings_bp.route('/api/meeting-requests/<int:meeting_id>/accept', methods=['POST'])
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
