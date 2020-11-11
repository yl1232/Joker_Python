from flask import Blueprint, request, jsonify
from model.room import Room
from model.room_state import RoomState
from server.database.db_methods import DBMethods
from server.api.authentication_api import token_required
import uuid
from common.rooms_api_errors import RoomsAPIErrors

rooms_api = Blueprint('rooms_api', __name__)


@rooms_api.route("/rooms", methods=['GET'])
@token_required
def get_rooms(current_player):
    rooms_as_dicts = {}
    index = 1
    rooms_as_objects = DBMethods.get_available_rooms_from_db()
    for room_as_object in rooms_as_objects:
        rooms_as_dicts[index] = room_as_object.to_dict()
        index += 1
    return jsonify(rooms_as_dicts)


@rooms_api.route("/rooms/<room_name>", methods=['GET'])
@token_required
def get_room(current_player, room_name):
    room = DBMethods.get_room_details_from_db(room_name)
    if room is None:
        room = {}
        return jsonify(room)
    else:
        return jsonify(room.to_dict())


@rooms_api.route("/rooms", methods=['POST'])
@token_required
def host_room(current_player):
    data = request.json
    room_name = data['room_name']
    if DBMethods.check_if_room_with_same_name_already_exists(room_name):
        return jsonify({'result': RoomsAPIErrors.ROOM_NAME_OCCUPIED.value})
    if DBMethods.check_if_player_already_in_a_room(current_player.username):
        return jsonify({'result': RoomsAPIErrors.PLAYER_ALREADY_IN_A_ROOM.value})
    room_id = str(uuid.uuid4())
    room = Room(room_id, room_name, RoomState.WAITING.value, [current_player], current_player)
    DBMethods.add_room_to_db(room)
    DBMethods.update_player_linked_room_in_db(current_player.username, room_id)
    return jsonify({'result': 'success'})


@rooms_api.route("/rooms/<room_name>/join", methods=['POST'])
@token_required
def join_room(current_player, room_name):
    room_name_from_player_input = room_name
    if DBMethods.check_if_player_already_in_a_room(current_player.username):
        return jsonify({'result': RoomsAPIErrors.PLAYER_ALREADY_IN_A_ROOM.value})
    rooms = DBMethods.get_available_rooms_from_db()
    for room in rooms:
        if room.name == room_name_from_player_input:
            if room.state == RoomState.PLAYING.value:
                return jsonify({'result': RoomsAPIErrors.ROOM_IN_PLAYING_STATE.value})
            DBMethods.update_player_linked_room_in_db(current_player.username, room.id)
            return jsonify({'result': 'success'})
    return jsonify({'result': RoomsAPIErrors.ROOM_NAME_DOESNT_EXIST.value})


@rooms_api.route("/rooms/<room_name>/leave", methods=['POST'])
@token_required
def leave_room(current_player, room_name):
    if not DBMethods.check_if_room_with_same_name_already_exists(room_name):
        return jsonify({'result': RoomsAPIErrors.ROOM_NAME_DOESNT_EXIST.value})
    room_details = DBMethods.get_room_details_from_db(room_name)
    room_id = room_details['id']
    if not DBMethods.check_if_player_in_room(current_player.username, room_id):
        return jsonify({'result': RoomsAPIErrors.PLAYER_NOT_IN_THE_ROOM.value})
    DBMethods.update_player_linked_room_in_db(current_player.username, None)
    return jsonify({'result': 'success'})
