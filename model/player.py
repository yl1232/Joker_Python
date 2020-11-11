class Player:
    def __init__(self, player_id, username, password):
        self.id = player_id
        self.username = username
        self.password = password

    def to_dict(self):
        return self.__dict__

    @classmethod
    def dict_to_obj(cls, player_as_dict):
        player_username = player_as_dict['username']
        player_id = player_as_dict['id']
        player_password = player_as_dict['password']
        player = cls(player_id, player_username, player_password)
        return player





