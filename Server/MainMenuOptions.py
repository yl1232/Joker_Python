import enum


class MainMenuOptions(enum.Enum):
    DISPLAY_AVAILABLE_ROOMS = "Display available rooms"
    DISPLAY_ROOM_DETAILS = "Display details of a room by room name"
    HOST_A_ROOM = "Host a room"
    JOIN_A_ROOM = "Join a room"
    LEAVE_A_ROOM = "Leave a room"
