from flask import Flask, request
import json
import sqlite3
import uuid
import contextlib
from SharedResources.player import Player
from SharedResources.room import Room
from SharedResources.roomstate import RoomState


app = Flask(__name__)


def create_db_tables():
    create_players_table()
    create_rooms_table()


def create_players_table():
    db_connection = get_db_connection()
    query = "CREATE TABLE IF NOT EXISTS players (" \
            "id TEXT PRIMARY KEY," \
            "name TEXT NOT NULL," \
            "room_id TEXT" \
            ");"
    db_connection.cursor().execute(query)
    db_connection.close()


def create_rooms_table():
    db_connection = get_db_connection()
    query = "CREATE TABLE IF NOT EXISTS rooms (" \
            "id TEXT PRIMARY KEY," \
            "name TEXT NOT NULL," \
            "state TEXT NOT NULL," \
            "host_id TEXT NOT NULL" \
            ");"
    db_connection.cursor().execute(query)
    db_connection.close()


def get_db_connection():
    db_connection = sqlite3.connect("C:\\Users\\yl1232\\PycharmProjects\\Joker\\Server\\Database\\database.db")
    db_connection.row_factory = row_tuple_to_dict
    return db_connection


def row_tuple_to_dict(cursor, row):
    row_as_dict = {}
    for index, column in enumerate(cursor.description):
        row_as_dict[column[0]] = row[index]
    return row_as_dict


@app.route("/")
def main_menu():
    menu_options_string = f"Please choose one of the following options:\n" \
           f"1. Display available game rooms\n" \
           f"2. Host a room\n" \
           f"3. Join a room\n" \
           f"4. Leave a room"
    menu_options_json = json.dumps(menu_options_string)
    return menu_options_json


@app.route("/rooms")
def get_available_rooms():
    rooms_as_dict = {}
    room_index = 1
    rooms = get_available_rooms_from_db()
    for room in rooms:
        rooms_as_dict[room_index] = room.to_dict()
        room_index += 1
    rooms_in_json_format = json.dumps(rooms_as_dict)
    return rooms_in_json_format


def get_available_rooms_from_db():
    with contextlib.closing(get_db_connection()) as db_connection:
        query = "SELECT * FROM rooms"
        result = db_connection.cursor().execute(query)
        rooms_as_dicts = result.fetchall()  # fetches list of dictionaries
        rooms_as_obj = []
        for room_as_dict in rooms_as_dicts:
            room_as_obj = room_dict_to_obj(room_as_dict)
            rooms_as_obj.append(room_as_obj)
        return rooms_as_obj


def room_dict_to_obj(room_as_dict):
    room_id = room_as_dict["id"]
    room_name = room_as_dict["name"]
    room_state = room_as_dict["state"]
    host_id = room_as_dict["host_id"]
    players_in_room = get_players_in_room_from_db(room_id)
    host_of_room = get_host_of_room_by_host_id(host_id, players_in_room)
    room_as_obj = Room(room_id, room_name, room_state, players_in_room, host_of_room)
    return room_as_obj


def get_host_of_room_by_host_id(room_host_id, players_in_room):
    for player in players_in_room:
        if player.id == room_host_id:
            return player


def get_players_in_room_from_db(room_id):
    with contextlib.closing(get_db_connection()) as db_connection:
        query = "SELECT * FROM players WHERE room_id=?"
        result = db_connection.cursor().execute(query, (room_id,))
        players_as_obj = []
        players_as_dict = result.fetchall()
        for player_as_dict in players_as_dict:
            player_name = player_as_dict["name"]
            player_id = player_as_dict["id"]
            player_as_obj = Player(player_id, player_name)
            players_as_obj.append(player_as_obj)
        return players_as_obj


@app.route("/host_a_room", methods=['POST'])
def host_a_room():
    data = request.json
    room_name = data['room_name']
    player = create_player_object_from_dict(data)
    if is_room_with_same_name_already_exists(room_name):
        return "There is already a room with this name"
    if is_the_player_already_in_a_room(player.id):
        return "You are already in one of the rooms"
    room_id = str(uuid.uuid4())
    room = Room(room_id, room_name, RoomState.WAITING.value, [player], player)
    add_room_to_db(room)
    add_player_to_db(player, room_id)
    return "Your room has been created successfully"


def create_player_object_from_dict(data):
    player_name = data['player_details']['name']
    player_id = data['player_details']['id']
    player = Player(player_id, player_name)
    return player


def add_room_to_db(room):
    with contextlib.closing(get_db_connection()) as db_connection:
        with db_connection as current_transaction:
            query = "INSERT INTO rooms(id, name, state, host_id) VALUES(?, ?, ?, ?);"
            current_transaction.execute(query, (room.id, room.name, room.state, room.host.id))


def add_player_to_db(player, room_id):
    with contextlib.closing(get_db_connection()) as db_connection:
        with db_connection as current_transaction:
            query = "INSERT INTO players(id, name, room_id) VALUES(?, ?, ?);"
            current_transaction.execute(query, (player.id, player.name, room_id))


def is_room_with_same_name_already_exists(room_name):
    with contextlib.closing(get_db_connection()) as db_connection:
        query = "SELECT name FROM rooms WHERE name=?"
        result = db_connection.cursor().execute(query, (room_name,))
        if result.fetchone() is None:
            return False
        return True


def is_the_player_already_in_a_room(player_id):
    with contextlib.closing(get_db_connection()) as db_connection:
        query = "SELECT * FROM players WHERE id=?"
        result = db_connection.cursor().execute(query, (player_id,))
        player_on_db = result.fetchone()
        if player_on_db is None:
            return False
        if player_on_db['room_id'] is None:
            return False
        return True


@app.route("/join_a_room", methods=['POST'])
def join_a_room():
    data = request.json
    room_name_from_player_input = data['room_name']
    player = create_player_object_from_dict(data)
    if is_the_player_already_in_a_room(player.id):
        return "You are already in one of the rooms"
    rooms = get_available_rooms_from_db()
    for room in rooms:
        if room.name == room_name_from_player_input:
            if room.state == RoomState.PLAYING.value:
                return "You can't join the room as there's a game being played there"
            if not is_player_in_db(player.id):
                add_player_to_db(player, room.id)
            update_player_linked_room_in_db(player.id, room.id)
            return f"You have successfully joined room {room_name_from_player_input}"
    return f"There's no room named {room_name_from_player_input}"


def is_player_in_db(player_id):
    with contextlib.closing(get_db_connection()) as db_connection:
        query = "SELECT * FROM players WHERE id=?"
        result = db_connection.cursor().execute(query, (player_id,))
        if result.fetchone() is None:
            return False
        return True


def update_player_linked_room_in_db(player_id, room_id):
    with contextlib.closing(get_db_connection()) as db_connection:
        with db_connection as current_transaction:
            query = "UPDATE players SET room_id=? WHERE id=?"
            current_transaction.cursor().execute(query, (room_id, player_id))


@app.route("/leave_a_room", methods=['POST'])
def leave_a_room():
    data = request.json
    player = create_player_object_from_dict(data)
    if not is_the_player_already_in_a_room(player.id):
        return "You are not in any room"
    update_player_linked_room_in_db(player.id, None)
    return "You have successfully left the room"


with app.app_context():
    create_db_tables()


if __name__ == "__main__":
    app.run(debug=True)
