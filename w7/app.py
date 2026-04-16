import connexion
from models import db

def create_app():
    # Khởi tạo FlaskApp từ connexion
    app = connexion.FlaskApp(__name__, specification_dir='static/')
    app.add_api('openapi.yaml', strict_validation=True, validate_responses=True)
    
    # Lấy Flask app instance để cấu hình SQLAlchemy
    flask_app = app.app
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Khởi tạo db với app
    db.init_app(flask_app)
    
    # Tạo bảng trong SQLite theo schema
    with flask_app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Chạy server ở cổng 5000
    app.run(host='127.0.0.1', port=5000)
