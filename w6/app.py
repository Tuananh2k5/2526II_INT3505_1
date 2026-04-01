from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-in-production'
app.config['REFRESH_SECRET_KEY'] = 'super-refresh-secret-key'

# Mock user database
USERS = {
    "admin": {
        "password": "password123", 
        "role": "admin", 
        "scopes": ["read", "write", "delete"]
    },
    "user1": {
        "password": "password123", 
        "role": "user", 
        "scopes": ["read"]
    }
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Bearer token format
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token is missing or invalid format!'}), 401
        
        token = auth_header.split(" ")[1]
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user']
            role = data.get('role')
            scopes = data.get('scopes', [])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, role, scopes, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = USERS.get(auth['username'])
    if not user or user['password'] != auth['password']:
        return jsonify({'message': 'Could not verify'}), 401
    
    # Generate Access Token (Short lived to prevent replay/leakage impact)
    access_token = jwt.encode({
        'user': auth['username'],
        'role': user['role'],
        'scopes': user['scopes'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    # Generate Refresh Token (Long lived)
    refresh_token = jwt.encode({
        'user': auth['username'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['REFRESH_SECRET_KEY'], algorithm="HS256")

    # Security Audit Issue Note: 
    # Returning token in response body is acceptable for SPA apps if stored in memory.
    # To prevent token leakage (XSS), HttpOnly cookies are recommended for web apps.
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@app.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    if not data or not data.get('refresh_token'):
        return jsonify({'message': 'Refresh token missing'}), 401
        
    try:
        data_decoded = jwt.decode(data['refresh_token'], app.config['REFRESH_SECRET_KEY'], algorithms=["HS256"])
        username = data_decoded['user']
        user = USERS.get(username)
        
        if not user:
            return jsonify({'message': 'User not found'}), 401
            
        access_token = jwt.encode({
            'user': username,
            'role': user['role'],
            'scopes': user['scopes'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'access_token': access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token is invalid!'}), 401

@app.route('/public', methods=['GET'])
def public_endpoint():
    return jsonify({'message': 'This is public data. No token required.'})

@app.route('/protected', methods=['GET'])
@token_required
def protected_endpoint(current_user, role, scopes):
    return jsonify({
        'message': f'Hello {current_user}, you are authorized.',
        'your_role': role,
        'your_scopes': scopes
    })

@app.route('/admin-only', methods=['GET'])
@token_required
def admin_endpoint(current_user, role, scopes):
    if role != 'admin':
        return jsonify({'message': 'Admin role required!'}), 403
    return jsonify({'message': 'Welcome Admin.'})

@app.route('/write-data', methods=['POST'])
@token_required
def write_data(current_user, role, scopes):
    if 'write' not in scopes:
        return jsonify({'message': 'Write scope required!'}), 403
    return jsonify({'message': 'Data written successfully.'})

# Insecure endpoint example (Token Leakage via GET URL parameter)
@app.route('/insecure-login', methods=['GET'])
def insecure_login():
    # Never pass credentials or return tokens in URL params (saved in browser history, logs)
    token = "example.leaked.token.do.not.use"
    return jsonify({
        'message': 'Warning: Token leaked in URL or logs if passed via GET', 
        'token': token
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
