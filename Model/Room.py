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

    def __str__(self):
        players_in_room = [player.username for player in self.players]
        return (f"Room name: {self.name}\n"
                f"Room state: {self.state}\n"
                f"Players: {players_in_room}\n"
                f"Host: {self.host.username}\n")

