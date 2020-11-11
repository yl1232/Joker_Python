from flask import Flask
from server.api.rooms_api import rooms_api
from server.api.authentication_api import authentication_api
from server.database.db_methods import DBMethods


app = Flask(__name__)
app.config.from_pyfile('config.py')
app.register_blueprint(rooms_api)
app.register_blueprint(authentication_api)


def create_db_tables():
    DBMethods.create_players_table()
    DBMethods.create_rooms_table()


with app.app_context():
    create_db_tables()


if __name__ == "__main__":
    app.run(debug=True)
