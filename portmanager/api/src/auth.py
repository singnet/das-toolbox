from flask import request, jsonify, current_app

def token_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {current_app.config['API_TOKEN']}":
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
