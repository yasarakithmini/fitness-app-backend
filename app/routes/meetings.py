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


# @meetings_bp.route('/api/meeting-requests/<trainer_id>', methods=['GET'])
# def get_meeting_requests(trainer_id):
#     try:
#         cursor = mysql.connection.cursor()
#         cursor.execute('''
#             SELECT * FROM meetings WHERE trainer_id = %s
#         ''', (trainer_id,))
#         meetings = cursor.fetchall()
#         cursor.close()
#
#         return jsonify(meetings), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@meetings_bp.route('/api/meeting-requests/<trainer_id>', methods=['GET'])
def get_pending_meetings(trainer_id):
    try:
        # Get the database connection from mysql
        cursor = mysql.connection.cursor()

        # Query to fetch pending meetings for a specific trainer
        query = "SELECT * FROM meetings WHERE trainer_id = %s AND status = 'pending'"
        cursor.execute(query, (trainer_id,))

        # Fetch all results
        meetings = cursor.fetchall()

        # Convert the results to dictionaries manually
        meetings_list = []
        for meeting in meetings:
            meetings_dict = {
                'id': meeting[0],
                'trainer_id': meeting[1],
                'user_id': meeting[2],
                'date_time': meeting[3],
                'status': meeting[4],
                # Add other columns as necessary
            }
            meetings_list.append(meetings_dict)

        # Close the cursor after use
        cursor.close()

        # Return the meetings data in JSON format
        return jsonify({'data': meetings_list}), 200

    except Exception as e:
        print("Error fetching meeting requests:", e)
        return jsonify({'error': 'Failed to fetch meeting requests'}), 500

@meetings_bp.route('/api/accepted-meetings/<trainer_id>', methods=['GET'])
def get_accepted_meetings(trainer_id):
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM meetings WHERE trainer_id = %s AND status = 'accepted'"
        cursor.execute(query, (trainer_id,))
        meetings = cursor.fetchall()

        meetings_list = []
        for meeting in meetings:
            meetings_dict = {
                'id': meeting[0],
                'trainer_id': meeting[1],
                'user_id': meeting[2],
                'date_time': meeting[3],
                'status': meeting[4],
            }
            meetings_list.append(meetings_dict)

        cursor.close()
        return jsonify({'data': meetings_list}), 200

    except Exception as e:
        print("Error fetching accepted meetings:", e)
        return jsonify({'error': 'Failed to fetch accepted meetings'}), 500


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

@meetings_bp.route('/api/meeting-requests/<int:meeting_id>/reject', methods=['POST'])
def reject_meeting(meeting_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''
        UPDATE meetings
        SET status = %s
        WHERE id = %s
    ''', ('rejected', meeting_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'id': meeting_id, 'status': 'rejected'}), 200

@meetings_bp.route('/api/user-accepted-meetings/<user_id>', methods=['GET'])
def get_user_accepted_meetings(user_id):
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM meetings WHERE user_id = %s AND status = 'accepted'"
        cursor.execute(query, (user_id,))
        meetings = cursor.fetchall()

        meetings_list = []
        for meeting in meetings:
            meetings_dict = {
                'id': meeting[0],
                'trainer_id': meeting[1],
                'user_id': meeting[2],
                'date_time': meeting[3],
                'status': meeting[4],
            }
            meetings_list.append(meetings_dict)

        cursor.close()
        return jsonify({'data': meetings_list}), 200

    except Exception as e:
        print("Error fetching user accepted meetings:", e)
        return jsonify({'error': 'Failed to fetch accepted meetings'}), 500

