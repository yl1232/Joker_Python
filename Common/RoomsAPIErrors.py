import enum


class RoomsAPIErrors(enum.Enum):
    ROOM_NAME_OCCUPIED = "There is already a room with this name. Please insert another name"
    PLAYER_ALREADY_IN_A_ROOM = "You are already in one of the rooms"
    ROOM_IN_PLAYING_STATE = "You can't join the room as there's a game being played there"
    ROOM_NAME_DOESNT_EXIST = "The room name you have entered doesn't exist"
