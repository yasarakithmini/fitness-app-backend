from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('app.config.Config')
    mysql.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.trainers import trainers_bp
    from app.routes.meetings import meetings_bp
    from app.routes.bmi import bmi_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.profile import profile_bp
    from app.routes.contact import contact_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(bmi_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(profile_bp)

    return app
