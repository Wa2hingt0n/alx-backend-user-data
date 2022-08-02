#!/usr/bin/env python3
""" Defines a function 'filter_datum' """
import logging
import mysql.connector
from os import getenv
import re
from typing import List


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
        fields: List[str],
        redaction: str,
        message: str,
        separator: str) -> str:
    """ Returns a log message that has been obfuscated

    Args:
        fields: A list of strings representing all fields to obfuscate
        redaction: a string representing by what the field will be obfuscated
        message: a string representing the log line
        separator: a string representing by which character is separating all
            fields in the log line (message)
    """
    for field in fields:
        regex = '(?<=' + field + '=).*?(?=;)'
        message = re.sub(regex, redaction, message)
    return message


def get_logger() -> logging.Logger:
    """ Creates and returns a logging.Logger object """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Connects to a MySQL database and returns a connector to the database"""
    hostname = getenv("PERSONAL_DATA_DB_HOST")
    db = getenv("PERSONAL_DATA_DB_NAME")
    usr_name = getenv("PERSONAL_DATA_DB_USERNAME")
    passwrd = getenv("PERSONAL_DATA_DB_PASSWORD")
    connector_variables = {"host": hostname,
                           "database": db,
                           "username": usr_name,
                           "password": passwrd
    }
    try:
        connection = mysql.connector.connect(**connector_variables)
        return connection
    except mysql.connector.Error as e:
        print("Error: ", e)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Formats the log record """
        formatted_record = super(RedactingFormatter, self).format(record)
        logged_record = filter_datum(self.fields, self.REDACTION,
                                     formatted_record,
                                     self.SEPARATOR)
        return logged_record
