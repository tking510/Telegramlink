from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.slot import slot_bp
from src.routes.line import line_bp
import os
import sys

# DON'T CHANGE: Add parent directory to path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

app = Flask(__name__, static_folder=\'static\', static_url_path=\'/\')
CORS(app) # Enable CORS for all routes

# Database configuration
app.config[\'SQLALCHEMY_DATABASE_URI\'] = \'sqlite:///slot_game.db\'
app.config[\'SQLALCHEMY_TRACK_MODIFICATIONS\'] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix=\'/api\')
app.register_blueprint(slot_bp, url_prefix=\'/api\')
app.register_blueprint(line_bp, url_prefix=\'/api\')

# Create database tables if they don\'t exist
with app.app_context():
    db.create_all()

@app.route(\'/\')
def serve_index():
    return send_from_directory(app.static_folder, \'index.html\')

@app.route(\'/<path:path>\')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == \'__main__\':
    app.run(debug=True, host=\'0.0.0.0\', port=5000)
