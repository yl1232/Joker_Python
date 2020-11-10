import enum


class AuthenticationErrors(enum.Enum):
    MISSING_LOGIN_DETAILS = "There are missing login details (username / password). Please try again "
    USERNAME_DOESNT_EXIST = "The username does not exist. Please try again"
    WRONG_PASSWORD = "Wrong password. Please try again"
    USERNAME_ALREADY_EXIST = "The username already exist. Please log in or register using a different username"
