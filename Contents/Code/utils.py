# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime
from os import path

from requests.utils import CaseInsensitiveDict

from constants import CHINESE_SUBTITLE


def parse_date(s):
    # noinspection PyBroadException
    try:
        return datetime.strptime(
            re.findall(r'\d{4}-\d{2}-\d{2}', s)[0], '%Y-%m-%d')
    except:
        return datetime(1, 1, 1)  # default value


def parse_table(s):
    table = CaseInsensitiveDict()
    for kv in s.split(','):
        if kv.count('=') > 0 and not kv.startswith('='):
            i = kv.find('=')
            table[kv[:i]] = kv[i + 1:]
    return table


def table_substitute(table, items):
    return [table[i] if i in table else i for i in items]


def has_tag(s, *tags):
    values = [i.upper() for i in re.split(r'[-_\s]', s)]
    return any(tag in values for tag in tags)


def has_embedded_chinese_subtitle(video_name):
    name, _ = path.splitext(
        path.basename(video_name))

    return CHINESE_SUBTITLE in name or has_tag(name, 'C', 'UC', 'CH')


def has_external_chinese_subtitle(video_name, *filenames):
    if not filenames:
        if not path.exists(video_name):
            return False
        return has_external_chinese_subtitle(video_name, *os.listdir(path.dirname(video_name)))

    basename, _ = path.splitext(
        path.basename(video_name))
    r = re.compile(
        r'\.(chinese|ch[ist]|zh(-(cn|hk|tw|hans|hant))?)\.(ass|srt|ssa|stl|sub|vid|vtt)$', re.IGNORECASE)
    for filename in filenames:
        if r.search(filename) and r.sub('', filename) == basename:
            return True
    return False


def has_chinese_subtitle(video_name):
    return has_embedded_chinese_subtitle(video_name) or \
        has_external_chinese_subtitle(video_name)
