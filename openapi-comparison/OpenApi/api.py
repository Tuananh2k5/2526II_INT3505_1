from flask import abort

# Simple in-memory database
USERS = {
    1: {"id": 1, "name": "Alice Smith", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob Jones", "email": "bob@example.com"}
}
NEXT_ID = 3

def get_users():
    return list(USERS.values())

def create_user(body):
    global NEXT_ID
    user_id = NEXT_ID
    NEXT_ID += 1
    new_user = {
        "id": user_id,
        "name": body.get("name"),
        "email": body.get("email")
    }
    USERS[user_id] = new_user
    return new_user, 201

def get_user(user_id):
    if user_id in USERS:
        return USERS[user_id]
    else:
        abort(404, f"User {user_id} not found")

def update_user(user_id, body):
    if user_id in USERS:
        USERS[user_id]["name"] = body.get("name", USERS[user_id]["name"])
        USERS[user_id]["email"] = body.get("email", USERS[user_id]["email"])
        return USERS[user_id]
    else:
        abort(404, f"User {user_id} not found")

def delete_user(user_id):
    if user_id in USERS:
        del USERS[user_id]
        return "", 204
    else:
        abort(404, f"User {user_id} not found")
