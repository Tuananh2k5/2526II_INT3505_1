import os
from datetime import timedelta

class Config:
    # Basic Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-super-secret-key')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-super-secret-key')
    JWT_ALGORITHM = 'HS256' # Chỉ định rõ thuật toán ký mạnh
    
    # Thời gian sống của token: access token ngắn (10 phút), refresh token dài (7 ngày)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # Vị trí lưu JWT: Access token gửi qua header, Refresh token lưu trong Cookie HttpOnly
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    
    # Giới hạn đường dẫn để gửi refresh cookie
    JWT_REFRESH_COOKIE_PATH = '/refresh'
    
    # Cấu hình an toàn cho Cookie (trong thực tế production sử dụng mạng HTTPS thì đặt True)
    JWT_COOKIE_SECURE = False 
    
    # Tạm tắt CSRF token cho cookie trong môi trường test (có thể bật nếu cấu trúc frontend yêu cầu)
    JWT_COOKIE_CSRF_PROTECT = False
