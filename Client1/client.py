import requests
import uuid
from SharedResources.player import Player
from SharedResources.room import Room
from Client1.menuoptions import MenuOptions


class Client:
    def __init__(self):
        player_name = input("Please insert your name: ")
        player_id = str(uuid.uuid4())
        self.player = Player(player_id, player_name)

    def main(self):
        self.display_main_menu()

    def display_main_menu(self):  # Use enum
        response = requests.get("http://127.0.0.1:5000/")
        menu_options = response.json()
        print(menu_options)
        player_choice = input()
        if player_choice == '1':
            self.display_available_rooms()
        elif player_choice == '2':
            self.host_a_room()
        elif player_choice == '3':
            self.join_a_room()
        elif player_choice == '4':
            self.leave_a_room()

    def display_available_rooms(self):
        rooms = self.get_available_rooms()
        print("These are the available game rooms:\n")
        for room in rooms:
            print(room)
        self.display_main_menu()

    def get_available_rooms(self):
        response = requests.get("http://127.0.0.1:5000/rooms")
        rooms_as_dict = response.json()
        rooms_as_obj = [self.room_dict_to_obj(room_as_dict) for room_as_dict in rooms_as_dict.values()]
        return rooms_as_obj

    def host_a_room(self):
        room_name = input("Please insert the name of the room: ")
        print("")
        data = {'room_name': room_name, 'player_details': self.player.to_dict()}
        response = requests.post("http://127.0.0.1:5000/host_a_room", json=data)
        print(f"{response.text}\n")
        self.display_main_menu()

    def join_a_room(self):
        room_name = input("Please insert the name of the room you want to join to: ")
        data = {'room_name': room_name, 'player_details': self.player.to_dict()}
        response = requests.post("http://127.0.0.1:5000/join_a_room", json=data)
        print(f"{response.text}\n")
        self.display_main_menu()

    def leave_a_room(self):
        data = {'player_details': self.player.to_dict()}
        response = requests.post("http://127.0.0.1:5000/leave_a_room", json=data)
        print(f"{response.text}\n")
        self.display_main_menu()

    def player_dict_to_obj(self, player_as_dict):
        player_name = player_as_dict['name']
        player_id = player_as_dict['id']
        player = Player(player_id, player_name)
        return player

    def room_dict_to_obj(self, room_as_dict):
        room_id = room_as_dict['id']
        room_name = room_as_dict['name']
        room_state = room_as_dict['state']
        room_players = [self.player_dict_to_obj(player_as_dict) for player_as_dict in room_as_dict['players']]
        room_host = self.player_dict_to_obj(room_as_dict['host'])
        room = Room(room_id, room_name, room_state, room_players, room_host)
        return room


def main():
    client = Client()
    client.display_main_menu()


if __name__ == "__main__":
    main()
