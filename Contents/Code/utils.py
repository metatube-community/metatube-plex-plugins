# -*- coding: utf-8 -*-

from re import findall
from datetime import datetime


def parse_date(s):
    # noinspection PyBroadException
    try:
        return datetime.strptime(
            findall(r'\d{4}-\d{2}-\d{2}', s)[0], '%Y-%m-%d')
    except:
        return datetime(1, 1, 1)  # default value
