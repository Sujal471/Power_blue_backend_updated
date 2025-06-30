from .chat_routes import chat_bp
from .upload_routes import upload_bp
from .history_routes import history_bp
from .change_password_routes import change_password_bp

def register_routes(app):
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(history_bp, url_prefix="/chat_history")
    app.register_blueprint(change_password_bp, url_prefix="/change_pass")