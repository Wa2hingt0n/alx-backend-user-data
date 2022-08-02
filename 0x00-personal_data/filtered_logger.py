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
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Connects to a MySQL database and returns a connector to the database"""
    hostname = getenv("PERSONAL_DATA_DB_HOST")
    db = getenv("PERSONAL_DATA_DB_NAME")
    usr_name = getenv("PERSONAL_DATA_DB_USERNAME")
    passwrd = getenv("PERSONAL_DATA_DB_PASSWORD")
    connector_variables = {"host": hostname,
                           "database": db,
                           "username": usr_name,
                           "password": passwrd}
    try:
        connection = mysql.connector.connect(**connector_variables)
        return connection
    except mysql.connector.Error as e:
        print("Error: ", e)


def main() -> None:
    """ Script main function """
    columns = ["name", "email", "phone", "ssn",
               "password", "ip", "last_login", "user_agent"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for row in cursor:
        series = map(lambda x: "{}={}".format(x[0], x[1]), zip(columns, row))
        log_message = "{}".format("; ".join(list(series)))
        log_record = logging.LogRecord(
            "user_data", logging.INFO, None, None, log_message, None, None)
        logger.handle(log_record)
    cursor.close()
    db.close()


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


if __name__ == "__main__":
    main()
