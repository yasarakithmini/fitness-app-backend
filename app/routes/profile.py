from flask import Blueprint, request, jsonify
from app import mysql

profile_bp = Blueprint('profile', __name__)
@profile_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, first_name, last_name, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'}), 404

@profile_bp.route('/user/update/<user_id>', methods=['POST'])
def update_user(user_id):
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    cursor = mysql.connection.cursor()
    cursor.execute('''
        UPDATE users
        SET first_name = %s, last_name = %s, email = %s
        WHERE id = %s
    ''', (first_name, last_name, email, user_id))

    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'User updated successfully!'})
