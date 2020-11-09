from Server.Database.DBMethods import DBMethods


class Player:
    def __init__(self, player_id, username, password):
        self.id = player_id
        self.username = username
        self.password = password

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def create_object_from_details_in_db(player_username):
        player_as_dict = DBMethods.get_player_details_from_db(player_username)
        if not player_as_dict:
            return False
        player_id = player_as_dict['id']
        player_password = player_as_dict['password']
        player_as_object = Player(player_id, player_username, player_password)
        return player_as_object





