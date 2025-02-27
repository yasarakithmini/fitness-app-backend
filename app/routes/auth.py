from flask import Blueprint, request, jsonify
import bcrypt
from app import mysql
import uuid
import MySQLdb



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
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

@auth_bp.route('/login', methods=['POST'])
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
