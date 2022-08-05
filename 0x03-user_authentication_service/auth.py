#!/usr/bin/env python3
""" Authentication script """
import bcrypt


def _hash_password(password: str) -> bytes:
    """ Generates a salted hash of the input password and returns it """
    passwrd = password.encode()
    hashed = bcrypt.hashpw(passwrd, bcrypt.gensalt())
    return hashed
