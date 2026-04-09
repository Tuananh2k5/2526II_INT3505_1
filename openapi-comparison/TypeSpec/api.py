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

def get_user(userId):
    if userId in USERS:
        return USERS[userId]
    else:
        abort(404, f"User {userId} not found")

def update_user(userId, body):
    if userId in USERS:
        USERS[userId]["name"] = body.get("name", USERS[userId]["name"])
        USERS[userId]["email"] = body.get("email", USERS[userId]["email"])
        return USERS[userId]
    else:
        abort(404, f"User {userId} not found")

def delete_user(userId):
    if userId in USERS:
        del USERS[userId]
        return "", 204
    else:
        abort(404, f"User {userId} not found")
