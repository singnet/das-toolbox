import jwt
from functools import wraps
from flask import request, jsonify, current_app

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.replace("Bearer ", "").strip()

        try:
            jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=[current_app.config["JWT_ALGORITHM"]]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return func(*args, **kwargs)

    return wrapper
