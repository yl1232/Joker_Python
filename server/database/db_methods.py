from server.database.db_connection import DBConnection
import contextlib
from model.player import Player
from model.room import Room


class DBMethods:
    @staticmethod
    def create_players_table():
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "CREATE TABLE IF NOT EXISTS players (" \
                    "id TEXT PRIMARY KEY NOT NULL," \
                    "username TEXT NOT NULL," \
                    "password TEXT NOT NULL," \
                    "room_id TEXT" \
                    ");"
            db_connection.cursor().execute(query)

    @staticmethod
    def create_rooms_table():
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "CREATE TABLE IF NOT EXISTS rooms (" \
                    "id TEXT PRIMARY KEY," \
                    "name TEXT NOT NULL," \
                    "state TEXT NOT NULL," \
                    "host_username TEXT NOT NULL" \
                    ");"
            db_connection.cursor().execute(query)

    @classmethod
    def get_available_rooms_from_db(cls):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM rooms"
            result = db_connection.cursor().execute(query)
            rooms_as_dicts = result.fetchall()
            rooms_as_objects = []
            for room_as_dict in rooms_as_dicts:
                room_as_object = cls.create_room_object_from_dict(room_as_dict)
                rooms_as_objects.append(room_as_object)
            return rooms_as_objects

    @classmethod
    def get_players_in_room_from_db(cls, room_id):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE room_id=?"
            result = db_connection.cursor().execute(query, (room_id,))
            players_as_dict = result.fetchall()
            return players_as_dict

    @classmethod
    def get_room_details_from_db(cls, room_name):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM rooms WHERE name=?"
            result = db_connection.cursor().execute(query, (room_name,))
            room_as_dict = result.fetchone()
            if room_as_dict is None:
                return room_as_dict
            room_as_object = cls.create_room_object_from_dict(room_as_dict)
            return room_as_object

    @staticmethod
    def add_room_to_db(room):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            with db_connection as current_transaction:
                query = "INSERT INTO rooms(id, name, state, host_username) VALUES(?, ?, ?, ?);"
                current_transaction.execute(query, (room.id, room.name, room.state, room.host.username))

    @staticmethod
    def add_new_player_to_db(player):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            with db_connection as current_transaction:
                query = "INSERT INTO players(id, username, password, room_id) VALUES(?, ?, ?, ?);"
                current_transaction.execute(query, (player.id, player.username, player.password, None))

    @staticmethod
    def check_if_room_with_same_name_already_exists(room_name):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT name FROM rooms WHERE name=?"
            result = db_connection.cursor().execute(query, (room_name,))
            if result.fetchone() is None:
                return False
            return True

    @staticmethod
    def check_if_player_already_in_a_room(player_username):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE username=?"
            result = db_connection.cursor().execute(query, (player_username,))
            player_details = result.fetchone()
            if player_details is None:
                return False
            if player_details['room_id'] is None:
                return False
            return True

    @staticmethod
    def check_if_player_exists(player_username):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE username=?"
            result = db_connection.cursor().execute(query, (player_username,))
            if result.fetchone() is None:
                return False
            return True

    @staticmethod
    def update_player_linked_room_in_db(player_username, room_id):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            with db_connection as current_transaction:
                query = "UPDATE players SET room_id=? WHERE username=?"
                current_transaction.cursor().execute(query, (room_id, player_username))

    @staticmethod
    def get_player_details_from_db(player_username):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE username=?"
            result = db_connection.cursor().execute(query, (player_username,))
            player_as_dict = result.fetchone()
            if player_as_dict is None:
                return None
            player_id = player_as_dict['id']
            player_password = player_as_dict['password']
            player_as_object = Player(player_id, player_username, player_password)
            return player_as_object

    @staticmethod
    def check_if_player_in_room(player_username, room_id):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE username=? AND room_id=?"
            result = db_connection.cursor().execute(query, (player_username, room_id))
            if result.fetchone() is None:
                return False
            return True

    @classmethod
    def create_room_object_from_dict(cls, room_as_dict):
        room_id = room_as_dict["id"]
        room_name = room_as_dict["name"]
        room_state = room_as_dict["state"]
        host_username = room_as_dict["host_username"]
        players_as_dict = cls.get_players_in_room_from_db(room_id)
        players_as_objects = []
        for player_as_dict in players_as_dict:
            player_id = player_as_dict['id']
            player_username = player_as_dict["username"]
            player_password = player_as_dict["password"]
            player_as_object = Player(player_id, player_username, player_password)
            players_as_objects.append(player_as_object)
        host_of_room = cls.get_host_of_room_by_host_username(host_username, players_as_objects)
        room_as_obj = Room(room_id, room_name, room_state, players_as_objects, host_of_room)
        return room_as_obj

    @classmethod
    def get_host_of_room_by_host_username(cls, host_username, players_in_room):
        for player in players_in_room:
            if player.username == host_username:
                return player
