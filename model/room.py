from model.player import Player


class Room:
    def __init__(self, room_id, name, state, players, host):
        self.id = room_id
        self.name = name
        self.state = state
        self.players = players
        self.host = host

    def to_dict(self):
        room_as_dict = {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "players": [player.to_dict() for player in self.players],
            "host": self.host.to_dict()
        }
        return room_as_dict

    @classmethod
    def dict_to_obj(cls, room_as_dict):
        room_id = room_as_dict['id']
        room_name = room_as_dict['name']
        room_state = room_as_dict['state']
        room_players = [Player.dict_to_obj(player_as_dict) for player_as_dict in room_as_dict['players']]
        room_host = Player.dict_to_obj(room_as_dict['host'])
        room = cls(room_id, room_name, room_state, room_players, room_host)
        return room

    def __str__(self):
        players_in_room = [player.username for player in self.players]
        return (f"Room name: {self.name}\n"
                f"Room state: {self.state}\n"
                f"Players: {players_in_room}\n"
                f"Host: {self.host.username}\n")

