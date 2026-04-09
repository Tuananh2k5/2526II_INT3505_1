from flask import Flask, request, jsonify, make_response, g
from flask_migrate import Migrate
from config import Config
from models import db, User, Item, TokenBlocklist
from schemas import UserSchema, ItemSchema
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt, set_refresh_cookies,
    unset_jwt_cookies
)
import bcrypt
from flasgger import Swagger
import functools

app = Flask(__name__)
app.config.from_object(Config)

# Cấu hình Security headers cơ bản (Content Security Policy) để hạn chế XSS
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
    return response

# Khởi tạo extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Khởi tạo Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header sử dụng Bearer scheme. Ví dụ: \"Bearer {token}\""
        }
    }
}
swagger = Swagger(app, config=swagger_config)

# Schema init
user_schema = UserSchema()
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

# ----------------- JWT Setup ------------------

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    """Kiểm tra token (access hoặc refresh) đã bị thu hồi hay chưa bằng JTI."""
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

# Các middleware / decorators kiểm tra roles và scopes (RBAC & Scope-based)
def require_role(role):
    """Kiểm tra quyền của người dùng dựa trên role (chứa trong claim 'role')."""
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify({"msg": "Không đủ quyền (role is insufficient)"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def require_scope(scope):
    """Kiểm tra quyền truy cập tài nguyên dựa trên scopes (chứa trong claim 'scopes')."""
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if scope not in claims.get("scopes", []):
                return jsonify({"msg": f"Thiếu scope yêu cầu: {scope}"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# ---------------- Auth Endpoints --------------

@app.route('/register', methods=['POST'])
def register():
    """
    Đăng ký người dùng
    Mật khẩu sẽ được mã hóa với bcrypt trước khi lưu.
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "123456"
            email:
              type: string
              example: "admin@example.com"
            role:
              type: string
              example: "admin"
            scopes:
              type: array
              items:
                type: string
              example: ["read:item", "write:item"]
    responses:
      201:
        description: Đăng ký thành công
      400:
        description: Tài khoản tồn tại hoặc dữ liệu lỗi
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
         return jsonify({"msg": "Thiếu dữ liệu"}), 400

    role = data.get('role', 'user')
    # Default có quyền read và write vào resources của chính mình, có thể tùy biến scope.
    scopes = data.get('scopes', ['read:item', 'write:item']) 

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"msg": "Username hoặc email đã tồn tại"}), 400

    # Hash password với số vòng lặp mặc định mạnh của bcrypt
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_pw, role=role)
    new_user.set_scopes(scopes)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Tạo user thành công", "user": user_schema.dump(new_user)}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập lấy Access Token & Refresh Token
    Access Token trả qua JSON, Refresh Token trả về qua Set-Cookie (HttpOnly).
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "123456"
    responses:
      200:
        description: Đăng nhập thành công, trả về tokens
      401:
        description: Sai tài khoản hoặc mật khẩu
    """
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"msg": "Sai username hoặc password"}), 401

    scopes = user.get_scopes()
    additional_claims = {
        "role": user.role,
        "scopes": scopes
    }
    
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id))

    response = jsonify({
        "access_token": access_token,
        "user": user_schema.dump(user)
    })
    
    set_refresh_cookies(response, refresh_token)
    return response, 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh Token Rotation
    Sử dụng cookie Refresh Token hợp lệ (trong HttpOnly Cookie) để tạo access và refresh token mới. 
    Thu hồi Refresh Token hiện tại để phòng Replay Attack.
    ---
    tags:
      - Auth
    responses:
      200:
        description: Cung cấp tokens mới
      401:
        description: Invalid refresh token
    """
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"msg": "Không tồn tại user"}), 404

    # Hủy refresh token hiện tại bằng JTI (Rotation)
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()

    additional_claims = {
        "role": user.role,
        "scopes": user.get_scopes()
    }
    
    new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    new_refresh_token = create_refresh_token(identity=identity)

    response = jsonify({"access_token": new_access_token})
    set_refresh_cookies(response, new_refresh_token)
    return response, 200

@app.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():
    """
    Đăng xuất: thu hồi token hiện tại
    Lưu JTI vào bảng blocklist. Thao tác này cũng xóa cookie đi kèm.
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Đã thu hồi token
    """
    token = get_jwt()
    jti = token["jti"]
    typeb = token["type"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()

    response = jsonify({"msg": f"Token loại {typeb} đã được thu hồi"})
    return response, 200

# ---------------- CRUD Items --------------

@app.route('/items', methods=['GET'])
@jwt_required()
@require_scope('read:item')
def get_items():
    """
    Lấy danh sách Item (Yêu cầu scope read:item)
    Hỗ trợ phân trang: truyền vào page và per_page.
    ---
    tags:
      - Item
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        example: 1
      - name: per_page
        in: query
        type: integer
        default: 10
        example: 10
    responses:
      200:
        description: Dữ liệu list các items + metadata phân trang
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    items_pg = Item.query.paginate(page=page, per_page=per_page, error_out=False)
    
    data = items_schema.dump(items_pg.items)
    
    return jsonify({
        "data": data,
        "total": items_pg.total,
        "pages": items_pg.pages,
        "current_page": page,
        "has_next": items_pg.has_next,
        "has_prev": items_pg.has_prev
    }), 200

@app.route('/items', methods=['POST'])
@jwt_required()
@require_scope('write:item')
def create_item():
    """
    Tạo Item (Yêu cầu scope write:item)
    ---
    tags:
      - Item
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Trà sữa chân trâu"
            description:
              type: string
              example: "Trà sữa trân châu full topping"
    responses:
      201:
        description: Tạo item mới thành công
    """
    data = request.get_json()
    errors = item_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    identity = get_jwt_identity()
    new_item = Item(name=data['name'], description=data.get('description'), owner_id=identity)
    db.session.add(new_item)
    db.session.commit()

    return jsonify(item_schema.dump(new_item)), 201

@app.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
@require_scope('read:item')
def get_item(item_id):
    """
    Lấy thông tin một Item theo ID (Yêu cầu scope read:item)
    ---
    tags:
      - Item
    security:
      - Bearer: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: OK
      404:
        description: Item không tồn tại
    """
    item = Item.query.get_or_404(item_id)
    return jsonify(item_schema.dump(item)), 200

@app.route('/items/<int:item_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@require_scope('write:item')
def update_item(item_id):
    """
    Sửa Item (Yêu cầu scope write:item)
    ---
    tags:
      - Item
    security:
      - Bearer: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Hồng trà Macchiato"
            description:
              type: string
              example: "Thêm nhiều kem cheese"
    responses:
      200:
        description: Cập nhật thành công
      404:
        description: Không tìm thấy
    """
    item = Item.query.get_or_404(item_id)
    
    # Chỉ chủ sở hữu mới có quyền update (hoặc admin)
    identity = get_jwt_identity()
    claims = get_jwt()
    if item.owner_id != int(identity) and claims.get('role') != 'admin':
        return jsonify({"msg": "Chỉ owner hoặc admin mới được sửa"}), 403

    data = request.get_json()
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']

    db.session.commit()
    return jsonify(item_schema.dump(item)), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
@require_scope('write:item')
def delete_item(item_id):
    """
    Xóa Item (Đòi hỏi Role admin)
    Check Role admin để cấp quyền xóa.
    ---
    tags:
      - Item
    security:
      - Bearer: []
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Xóa thành công
      403:
        description: Cần role admin
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
         return jsonify({"msg": "Chỉ quản trị viên mới được phép xóa"}), 403

    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"msg": "Item deleted"}), 200

@app.route('/users', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_users():
    """
    Lấy danh sách người dùng (Chỉ ADMIN)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Users list
    """
    users = User.query.all()
    return jsonify(user_schema.dump(users, many=True)), 200

if __name__ == '__main__':
    # Có thể thêm ssl_context='adhoc' để chạy dev qua dạng HTTPS tạo bảo mật
    app.run(debug=True, port=8000)
