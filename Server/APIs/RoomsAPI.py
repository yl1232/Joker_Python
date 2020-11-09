from flask import Blueprint, request, jsonify
from Model.Player import Player
from Model.Room import Room
from Model.RoomState import RoomState
from Server.Database.DBMethods import DBMethods
from Server.APIs.AuthenticationAPI import token_required
import uuid

rooms_api = Blueprint('rooms_api', __name__)


@rooms_api.route("/rooms", methods=['GET'])
@token_required
def get_rooms(current_player):
    rooms_as_dicts = {}
    index = 1
    rooms_as_objects = get_available_rooms_as_objects()
    for room_as_object in rooms_as_objects:
        rooms_as_dicts[index] = room_as_object.to_dict()
        index += 1
    return jsonify(rooms_as_dicts)


@rooms_api.route("/rooms/<room_name>", methods=['GET'])
@token_required
def get_room(current_player, room_name):
    room_details = DBMethods.get_room_details_from_db(room_name)
    room_as_object = create_room_object_from_dict(room_details)
    return jsonify(room_as_object.to_dict())


@rooms_api.route("/rooms", methods=['POST'])
@token_required
def host_room(current_player):
    data = request.json
    room_name = data['room_name']
    if DBMethods.check_if_room_with_same_name_already_exists(room_name):
        return "There is already a room with this name"
    if DBMethods.check_if_player_already_in_a_room(current_player.username):
        return "You are already in one of the rooms"
    room_id = str(uuid.uuid4())
    room = Room(room_id, room_name, RoomState.WAITING.value, [current_player], current_player)
    DBMethods.add_room_to_db(room)
    DBMethods.update_player_linked_room_in_db(current_player.username, room_id)
    return "Your room has been created successfully"


@rooms_api.route("/rooms/<room_name>", methods=['PUT'])
@token_required
def join_room(current_player, room_name):
    room_name_from_player_input = room_name
    if DBMethods.check_if_player_already_in_a_room(current_player.username):
        return "You are already in one of the rooms"
    rooms = get_available_rooms_as_objects()
    for room in rooms:
        if room.name == room_name_from_player_input:
            if room.state == RoomState.PLAYING.value:
                return "You can't join the room as there's a game being played there"
            DBMethods.update_player_linked_room_in_db(current_player.username, room.id)
            return f"You have successfully joined room {room_name_from_player_input}"
    return f"There's no room named {room_name_from_player_input}"


# @rooms_api.route("/rooms/<room_name>", methods=['PUT'])
# def leave_room():
#     data = request.json
#     player = Player.create_player_object_from_dict(data)
#     if not DBMethods.check_if_player_already_in_a_room(player.id):
#         return "You are not in any room"
#     DBMethods.update_player_linked_room_in_db(player.id, None)
#     return "You have successfully left the room"


def get_available_rooms_as_objects():
    rooms_as_dicts = DBMethods.get_available_rooms_from_db()
    rooms_as_objects = []
    for room_as_dict in rooms_as_dicts:
        room_as_object = create_room_object_from_dict(room_as_dict)
        rooms_as_objects.append(room_as_object)
    return rooms_as_objects


def create_room_object_from_dict(room_as_dict):
    room_id = room_as_dict["id"]
    room_name = room_as_dict["name"]
    room_state = room_as_dict["state"]
    host_username = room_as_dict["host_username"]
    players_as_dict = DBMethods.get_players_in_room_from_db(room_id)
    players_as_objects = []
    for player_as_dict in players_as_dict:
        player_id = player_as_dict['id']
        player_username = player_as_dict["username"]
        player_password = player_as_dict["password"]
        player_as_object = Player(player_id, player_username, player_password)
        players_as_objects.append(player_as_object)
    host_of_room = get_host_of_room_by_host_username(host_username, players_as_objects)
    room_as_obj = Room(room_id, room_name, room_state, players_as_objects, host_of_room)
    return room_as_obj


def get_host_of_room_by_host_username(host_username, players_in_room):
    for player in players_in_room:
        if player.username == host_username:
            return player
