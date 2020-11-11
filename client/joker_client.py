import requests
from model.room import Room
from common.authentication_errors import AuthenticationErrors
from common.rooms_api_errors import RoomsAPIErrors
import client.constants as constants
from client.main_menu_options import MainMenuOptions


class Client:
    player_token = None

    @classmethod
    def main(cls):
        cls.display_authentication_menu()

    @classmethod
    def display_authentication_menu(cls):
        auth_menu = '''Welcome to Joker Game!
Please choose one of the following options:
1. Login
2. Register
'''
        player_choice = input(auth_menu)
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
        url = f"{constants.SERVER_DOMAIN}/login"
        response = requests.post(url, json=data)
        result = response.json()
        result_status = result['result']
        if result_status == 'success':
            cls.player_token = result['token']
            print("You have successfully logged in\n")
            cls.display_main_menu()
        else:
            print(f"{result_status}\n")
            if (result_status == AuthenticationErrors.MISSING_LOGIN_DETAILS.value) or \
               (result_status == AuthenticationErrors.WRONG_PASSWORD.value):
                cls.login()
            elif result_status == AuthenticationErrors.USERNAME_DOESNT_EXIST.value:
                cls.register()

    @classmethod
    def register(cls):
        print("Welcome to Registration page!\n")
        username = input("Please insert a username: ")
        password = input("Please insert a password: ")
        print("")
        data = {'username': username, 'password': password}
        url = f"{constants.SERVER_DOMAIN}/register"
        response = requests.post(url, json=data)
        result = response.json()
        result_status = result['result']
        if result_status == 'success':
            print("You have successfully registered\n")
        else:
            print(f"{result_status}\n")
        cls.display_authentication_menu()

    @classmethod
    def display_main_menu(cls):
        menu_options = [menu_option.value for menu_option in MainMenuOptions]
        menu_options_string = ""
        for counter, menu_option in enumerate(menu_options, 1):
            menu_options_string += f"{counter}. {menu_option}\n"
        player_choice = input(menu_options_string)
        if player_choice == '1':
            cls.display_available_rooms()
        elif player_choice == '2':
            cls.display_room_details_by_room_name()
        elif player_choice == '3':
            cls.host_room()
        elif player_choice == '4':
            cls.join_room()
        elif player_choice == '5':
            cls.leave_room()

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
        url = f"{constants.SERVER_DOMAIN}/rooms"
        headers = {'x-access-token': cls.player_token}
        response = requests.get(url, headers=headers)
        rooms_as_dict = response.json()
        rooms_as_obj = [Room.dict_to_obj(room_as_dict) for room_as_dict in rooms_as_dict.values()]
        return rooms_as_obj

    @classmethod
    def display_room_details_by_room_name(cls):
        room_name = input("Please insert the name of the room: ")
        print("")
        url = f"{constants.SERVER_DOMAIN}/rooms/{room_name}"
        headers = {'x-access-token': cls.player_token}
        response = requests.get(url, headers=headers)
        room_as_dict = response.json()
        if not room_as_dict:
            print(f"{RoomsAPIErrors.ROOM_NAME_DOESNT_EXIST.value}\n")
        else:
            room_as_obj = Room.dict_to_obj(room_as_dict)
            print(room_as_obj)
        cls.display_main_menu()

    @classmethod
    def host_room(cls):
        room_name = input("Please insert the name of the room: ")
        print("")
        data = {'room_name': room_name}
        url = f"{constants.SERVER_DOMAIN}/rooms"
        headers = {'x-access-token': cls.player_token}
        response = requests.post(url, headers=headers, json=data)
        request_result = response.json()['result']
        if request_result == 'success':
            print("Your room has been created successfully\n")
            cls.display_main_menu()
        else:
            print(f"{request_result}\n")
            if request_result == RoomsAPIErrors.ROOM_NAME_OCCUPIED.value:
                cls.host_room()
            else:
                cls.display_main_menu()

    @classmethod
    def join_room(cls):
        room_name = input("Please insert the name of the room you want to join to: ")
        url = f"{constants.SERVER_DOMAIN}/rooms/{room_name}/join"
        headers = {'x-access-token': cls.player_token}
        response = requests.post(url, headers=headers)
        request_result = response.json()['result']
        if request_result == 'success':
            print(f"You have successfully joined room \"{room_name}\"\n")
        else:
            print(f"{request_result}\n")
        cls.display_main_menu()

    @classmethod
    def leave_room(cls):
        room_name = input("Please insert the name of the room you want to leave: ")
        url = f"{constants.SERVER_DOMAIN}/rooms/{room_name}/leave"
        headers = {'x-access-token': cls.player_token}
        response = requests.post(url, headers=headers)
        request_result = response.json()['result']
        if request_result == 'success':
            print(f"You have successfully left room \"{room_name}\"\n")
        else:
            print(f"{request_result}\n")
        cls.display_main_menu()


def main():
    Client.main()


if __name__ == "__main__":
    main()
