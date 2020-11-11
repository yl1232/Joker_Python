from flask import request, jsonify, Blueprint, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from datetime import datetime, timedelta
from functools import wraps
from model.player import Player
from server.database.db_methods import DBMethods
from common.authentication_errors import AuthenticationErrors


authentication_api = Blueprint('authentication_api', __name__)


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_player = DBMethods.get_player_details_from_db(data['username'])
        except:
            return jsonify({
                'message': 'Token is invalid'
            }), 401
        return func(current_player, *args, **kwargs)
    return decorated


@authentication_api.route("/login", methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if not data or not username or not password:
        return jsonify({'result': AuthenticationErrors.MISSING_LOGIN_DETAILS.value})
    player = DBMethods.get_player_details_from_db(username)
    if not player:
        return jsonify({'result': AuthenticationErrors.USERNAME_DOESNT_EXIST.value})
    if check_password_hash(player.password, password):
        token = jwt.encode({
            'username': player.username,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        }, current_app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8'),
                        'result': 'success'})
    return jsonify({'result': AuthenticationErrors.WRONG_PASSWORD.value})


@authentication_api.route("/register", methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    player = DBMethods.get_player_details_from_db(username)
    if player is None:
        player_id = str(uuid.uuid4())
        player = Player(player_id, username, generate_password_hash(password))
        DBMethods.add_new_player_to_db(player)
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': AuthenticationErrors.USERNAME_ALREADY_EXIST.value})
