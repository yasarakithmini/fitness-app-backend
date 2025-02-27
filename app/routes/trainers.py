from flask import Blueprint, jsonify
from app import mysql
import MySQLdb

trainers_bp = Blueprint('trainers', __name__)

@trainers_bp.route('/api/trainers', methods=['GET'])
def get_trainers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(''' SELECT id, first_name, last_name FROM users WHERE user_type = %s ''', ('Trainer',))
    trainers = cursor.fetchall()
    cursor.close()

    trainer_data = [{"id": trainer['id'], "name": f"{trainer['first_name']} {trainer['last_name']}"} for trainer in trainers]

    return jsonify(trainer_data)
