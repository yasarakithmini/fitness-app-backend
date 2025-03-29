from flask import Blueprint, request, jsonify
from app import mysql
from MySQLdb.cursors import DictCursor
import bcrypt

profile_bp = Blueprint('profile', __name__)
@profile_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT id, first_name, last_name, email, user_type FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'}), 404

@profile_bp.route('/api/user/update/<user_id>', methods=['POST'])
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


@profile_bp.route('/api/user/change-password/<user_id>', methods=['POST'])
def change_password(user_id):
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'message': 'Missing required fields'}), 400

    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Compare old password with hashed password
    if not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({'message': 'Old password is incorrect'}), 401

    # Hash new password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'Password changed successfully!'})
