from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import uuid
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

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

    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO users (id, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s) ''', (user_id, first_name, last_name, email, password))
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
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
            'message': 'User logged in successfully!'
        })
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

if __name__ == '__main__':
    app.run(debug=True)
