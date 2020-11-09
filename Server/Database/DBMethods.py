from Server.Database.DBConnection import DBConnection
import contextlib


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

    @staticmethod
    def get_available_rooms_from_db():
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM rooms"
            result = db_connection.cursor().execute(query)
            rooms_as_dicts = result.fetchall()  # fetches list of dictionaries
            return rooms_as_dicts

    @staticmethod
    def get_players_in_room_from_db(room_id):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM players WHERE room_id=?"
            result = db_connection.cursor().execute(query, (room_id,))
            players_as_dict = result.fetchall()
            return players_as_dict

    @staticmethod
    def get_room_details_from_db(room_name):
        with contextlib.closing(DBConnection.get_connection()) as db_connection:
            query = "SELECT * FROM rooms WHERE name=?"
            result = db_connection.cursor().execute(query, (room_name,))
            room_as_dict = result.fetchone()
            return room_as_dict

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
            return player_as_dict
