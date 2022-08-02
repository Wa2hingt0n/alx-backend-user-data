#!/usr/bin/env python3
""" Defines a function hash_password """
import bcrypt


def hash_password(password: str) -> bytes:
    """ Returns a hashed salted byte string password of 'password' """
    passwrd = password.encode()
    hashed = bcrypt.hashpw(passwrd, bcrypt.gensalt())
    return hashed


def is_valid(hashed_password: bytes, password: str) -> bool:
    """ Validates whether password matches the hashed_password """
    passwrd = password.encode()
    if bcrypt.checkpw(passwrd, hashed_password):
        return True
    else:
        return False
