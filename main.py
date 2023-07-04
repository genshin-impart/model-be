from flask import Flask, jsonify, request, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'qwerty'

users = {
    'admin': {
        'pwd': generate_password_hash('admin'),
    },
    'clzh': {
        'pwd': generate_password_hash('123456'),
    },
}

@app.route('/')
def index():
    return 'Backend Server is on'

@app.route('/v1/login', methods=['POST'])
def login():
    usr_name = request.json.get('username')
    pwd = request.json.get('password')
    if (usr_name is None) or (pwd is None):
        abort(400, 'invalid login request')
    if (usr_name not in users) or (not check_password_hash(users[usr_name]['pwd'], pwd)):
        abort(403, 'invalid username or password')
    return jsonify({'code': '0', 'msg': 'success', 'username': usr_name})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)