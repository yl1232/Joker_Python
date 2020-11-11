import sqlite3


class DBConnection:
    connection = None

    def __init__(self):
        if self.connection is None:
            self.connection = self.connect()
        else:
            raise Exception("You cannot create another instance")

    @classmethod
    def get_connection(cls):
        if not cls.connection:
            cls()
        cls.connection = cls.connect()
        return cls.connection

    @classmethod
    def connect(cls):
        db_connection = sqlite3.connect("C:\\Users\\yl1232\\PycharmProjects\\Joker_Python\\server\\database\\database.db")
        db_connection.row_factory = cls.row_tuple_to_dict
        return db_connection

    @staticmethod
    def row_tuple_to_dict(cursor, row):
        row_as_dict = {}
        for index, column in enumerate(cursor.description):
            row_as_dict[column[0]] = row[index]
        return row_as_dict

