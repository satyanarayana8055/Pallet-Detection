from flask import Flask
import os
from api.routes import routes_bp
from config.config import Config


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_DIR
    app.config["MAX_CONTENT_LENGTH"] = Config.CONTENT_LEN

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprint
    app.register_blueprint(routes_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
x
