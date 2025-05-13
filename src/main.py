import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, render_template, session # Added session
from src.models.models import db, User, ServiceCategory, Service, Order 
from src.routes.auth_routes import auth_bp
from src.routes.services_routes import services_bp # Import the services blueprint

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), template_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'a_very_strong_and_unique_secret_key_for_atm_followr'

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(services_bp, url_prefix='/services') # Register services blueprint

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_user_session():
    # Injects session variables into the template context
    return dict(session=session)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    # Render specific HTML files if they are requested directly and exist in the static folder (acting as template folder)
    if path.endswith('.html') and os.path.exists(os.path.join(static_folder_path, path)):
        # Special handling for index.html to ensure it's the main entry point
        if path == "index.html" or path == "":
             return render_template('index.html')
        return render_template(path)
    
    # Serve other static files (CSS, JS, images)
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        # Default to index.html if path is empty or not found (SPA-like behavior)
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return render_template('index.html') # Use render_template for index.html as well
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

