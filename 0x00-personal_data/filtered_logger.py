#!/usr/bin/env python3
""" Defines a function 'filter_datum' """
import re
from typing import List


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
