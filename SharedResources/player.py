class Player:
    def __init__(self, player_id, name):
        self.id = player_id
        self.name = name

    def to_dict(self):
        return self.__dict__


