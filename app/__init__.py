from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Load configurations
    app.config.from_object('app.config.Config')  # Load the config file

    # Initialize MySQL
    mysql.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.trainers import trainers_bp
    from app.routes.meetings import meetings_bp
    from app.routes.bmi import bmi_bp
    from app.routes.recommendations import recommendations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(bmi_bp)
    app.register_blueprint(recommendations_bp)

    return app
