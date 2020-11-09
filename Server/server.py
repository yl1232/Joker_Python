from flask import Flask, jsonify
from Server.APIs.RoomsAPI import rooms_api
from Server.APIs.AuthenticationAPI import authentication_api
import json
from Server.mainmenuoptions import MainMenuOptions
from Server.Database.DBMethods import DBMethods


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(rooms_api)
app.register_blueprint(authentication_api)


def create_db_tables():
    DBMethods.create_players_table()
    DBMethods.create_rooms_table()


@app.route("/")
def authentication_menu():
    menu = f"1. Login\n" \
           f"2. Register\n"
    return jsonify(menu)


@app.route("/main")
def main_menu():
    menu_options = [menu_option.value for menu_option in MainMenuOptions]
    menu_options_string = ""
    for counter, menu_option in enumerate(menu_options, 1):
        menu_options_string += f"{counter}. {menu_option}\n"
    menu_options_json = json.dumps(menu_options_string)
    return menu_options_json


with app.app_context():
    create_db_tables()


if __name__ == "__main__":
    app.run(debug=True)
