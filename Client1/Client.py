import requests
from Model.Player import Player
from Model.Room import Room
from Common.AuthenticationErrors import AuthenticationErrors
from Common.RoomsAPIErrors import RoomsAPIErrors


class Client:
    player_token = None

    @classmethod
    def main(cls):
        cls.display_authentication_menu()

    @classmethod
    def display_authentication_menu(cls):
        auth_menu = f"Welcome to Joker Game!\n" \
                    f"Please choose one of the following options:\n" \
                    f"1. Login\n" \
                    f"2. Register\n"
        print(auth_menu)
        player_choice = input()
        if player_choice == '1':
            cls.login()
        elif player_choice == '2':
            cls.register()

    @classmethod
    def login(cls):
        print("Welcome to Login page!\n")
        username = input("Please insert your username: ")
        password = input("Please insert your password: ")
        print("")
        data = {'username': username, 'password': password}
        response = requests.post("http://127.0.0.1:5000/login", json=data)
        if (response.text == AuthenticationErrors.MISSING_LOGIN_DETAILS.value) or \
           (response.text == AuthenticationErrors.USERNAME_DOESNT_EXIST.value) or \
           (response.text == AuthenticationErrors.WRONG_PASSWORD.value):
            print(response.text)
            print("")
            cls.login()
        else:
            response_data = response.json()
            cls.player_token = response_data['token']
            print("You have successfully logged in\n")
            cls.display_main_menu()

    @classmethod
    def register(cls):
        print("Welcome to Registration page!\n")
        username = input("Please insert a username: ")
        password = input("Please insert a password: ")
        print("")
        data = {'username': username, 'password': password}
        response = requests.post("http://127.0.0.1:5000/register", json=data)
        print(response.text)
        cls.display_authentication_menu()

    @classmethod
    def display_main_menu(cls):
        response = requests.get("http://127.0.0.1:5000/")
        menu_options = response.json()
        print(menu_options)
        player_choice = input()
        if player_choice == '1':
            cls.display_available_rooms()
        elif player_choice == '2':
            cls.display_room_details_by_room_name()
        elif player_choice == '3':
            cls.host_a_room()
        elif player_choice == '4':
            cls.join_a_room()
        elif player_choice == '5':
            cls.leave_a_room()

    @classmethod
    def display_available_rooms(cls):
        rooms = cls.get_available_rooms()
        if not rooms:
            print("There are no available rooms\n")
        else:
            print("These are the available game rooms:\n")
            for room in rooms:
                print(room)
        cls.display_main_menu()

    @classmethod
    def get_available_rooms(cls):
        url = "http://127.0.0.1:5000/rooms"
        headers = {'x-access-token': cls.player_token}
        response = requests.get(url, headers=headers)
        rooms_as_dict = response.json()
        rooms_as_obj = [cls.room_dict_to_obj(room_as_dict) for room_as_dict in rooms_as_dict.values()]
        return rooms_as_obj

    @classmethod
    def display_room_details_by_room_name(cls):  # Need to check if room exists
        room_name = input("Please insert the name of the room: ")
        print("")
        url = "http://127.0.0.1:5000/rooms/" + room_name
        headers = {'x-access-token': cls.player_token}
        response = requests.get(url, headers=headers)
        room_as_dict = response.json()
        if not room_as_dict:
            print(RoomsAPIErrors.ROOM_NAME_DOESNT_EXIST.value)
        else:
            room_as_obj = cls.room_dict_to_obj(room_as_dict)
            print(room_as_obj)
        cls.display_main_menu()

    @classmethod
    def host_a_room(cls):
        room_name = input("Please insert the name of the room: ")
        print("")
        data = {'room_name': room_name}
        url = "http://127.0.0.1:5000/rooms"
        headers = {'x-access-token': cls.player_token}
        response = requests.post(url, headers=headers, json=data)
        print(f"{response.text}\n")
        if response.text == RoomsAPIErrors.ROOM_NAME_OCCUPIED.value:
            cls.host_a_room()
        else:
            cls.display_main_menu()

    @classmethod
    def join_a_room(cls):
        room_name = input("Please insert the name of the room you want to join to: ")
        url = "http://127.0.0.1:5000/rooms/" + room_name
        headers = {'x-access-token': cls.player_token}
        response = requests.put(url, headers=headers)
        print(f"{response.text}\n")
        cls.display_main_menu()

    @classmethod
    def leave_a_room(cls):
        response = requests.put("http://127.0.0.1:5000/leave_a_room")
        print(f"{response.text}\n")
        cls.display_main_menu()

    @classmethod
    def player_dict_to_obj(cls, player_as_dict):
        player_username = player_as_dict['username']
        player_id = player_as_dict['id']
        player_password = player_as_dict['password']
        player = Player(player_id, player_username, player_password)
        return player

    @classmethod
    def room_dict_to_obj(cls, room_as_dict):
        room_id = room_as_dict['id']
        room_name = room_as_dict['name']
        room_state = room_as_dict['state']
        room_players = [cls.player_dict_to_obj(player_as_dict) for player_as_dict in room_as_dict['players']]
        room_host = cls.player_dict_to_obj(room_as_dict['host'])
        room = Room(room_id, room_name, room_state, room_players, room_host)
        return room


def main():
    Client.main()


if __name__ == "__main__":
    main()
