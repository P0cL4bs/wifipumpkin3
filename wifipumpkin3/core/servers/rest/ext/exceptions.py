from flask import jsonify

def exception(error_message, code=200):
    response = jsonify({"code": code, "message": error_message})
    response.status_code = code
    return response