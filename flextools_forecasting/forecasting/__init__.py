from flask import Flask
from forecasting.models import db
from flask_cors import CORS

def create_app(config_filename="config.py"):
    """
    Create a Flask app with the given configuration file."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)  

    db.init_app(app)
    CORS(app)

    with app.app_context():
        db.create_all()
    
    # LayoutHandler.load_layout(app, app.config.get("LAYOUT_FILE"))

    from .blueprints.api import api_blueprint 
    # from .blueprints.ui import ui_blueprint

    # app.register_blueprint(ui_blueprint)
    app.register_blueprint(api_blueprint)

    return app

