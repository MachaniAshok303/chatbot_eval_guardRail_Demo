"""
app.py
------
Flask entry point. Run with:  python app.py
"""

from flask import Flask

from routes.chat_routes import chat_bp
from routes.eval_routes import eval_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(chat_bp)
    app.register_blueprint(eval_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
