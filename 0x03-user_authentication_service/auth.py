#!/usr/bin/env python3
""" Authentication script """
import bcrypt
import uuid
from db import DB
from sqlalchemy.orm.exc import NoResultFound
from typing import Union
from user import User


def _hash_password(password: str) -> bytes:
    """ Generates a salted hash of the input password and returns it """
    passwrd = password.encode()
    hashed = bcrypt.hashpw(passwrd, bcrypt.gensalt())
    return hashed


def _generate_uuid() -> str:
    """ Returns a string representation of a new uuid """
    new_id = uuid.uuid4()
    return str(new_id)


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            hashed = _hash_password(password)
            new_user = self._db.add_user(email, hashed)
            return new_user
        raise ValueError("User {} already exists".format(email))

    def valid_login(self, email: str, password: str) -> bool:
        """ Checks whether email and password provided are valid """
        try:
            user = self._db.find_user_by(email=email)
            if user and bcrypt.checkpw(
                    password.encode(), user.hashed_password):
                return True
        except NoResultFound:
            return False
        return False

    def create_session(self, email: str) -> Union[str, None]:
        """ Returns a session uuid string """
        try:
            user = self._db.find_user_by(email=email)
            if user:
                usr_session_id = _generate_uuid()
                self._db.update_user(user.id, session_id=usr_session_id)
                return usr_session_id
        except NoResultFound:
            return None
        return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """ Retrieves a user using the session id """
        if session_id:
            try:
                user = self._db.find_user_by(session_id=session_id)
                if user:
                    return user
            except NoResultFound:
                return None
        return None

    def destroy_session(self, user_id: int) -> None:
        """ Updates an existing session_id to None """
        if user_id is None:
            return None
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """ Generates a reset password token """
        user = None
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()
        reset_token = _generate_uuid()
        self._db.update_user(user.id, reset_token=reset_token)
        return reset_token

    def update_password(self, reset_token: str, password: str) -> None:
        """Find's user by  reset token and updates the hashed_password """
        user = None
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            user = None
        if user is None:
            raise ValueError()
        new_password = _hash_password(password)
        self._db.update_user(
            user.id, hashed_password=new_password, reset_token=None)
