# -*- coding: utf-8 -*-
import os
import re
from base64 import b64decode
from datetime import datetime

from constants import CHINESE_SUBTITLE

VIDEO_EXTENSIONS = ('.mp4', '.wmv', '.avi', '.rm', '.rmvb', '.m4v', 'webm',
                    '.ogg', '.mkv', '.flv', '.mov', '.3gp', '.ts', '.mpg')


def parse_date(s):
    # noinspection PyBroadException
    try:
        return datetime.strptime(
            re.findall(r'\d{4}-\d{2}-\d{2}', s)[0], '%Y-%m-%d')
    except:
        return datetime(1, 1, 1)  # default value


def parse_list(s):
    return [i.strip().upper() for i in s.split(',') if i.strip()]


def parse_table(s, sep=',', b64=False, origin_key=False):
    table = {}
    if not s:
        return table
    if b64:
        s = b64decode(s).decode('utf-8')
    for kv in s.split(sep):
        kv = kv.strip()  # trim all whitespaces
        if kv.count('=') > 0 and not kv.startswith('='):
            i = kv.find('=')
            table[(kv[:i] if origin_key else kv[:i].upper())] = kv[i + 1:]
    return table


def table_substitute(table, items):
    return [(table[i.upper()] if i.upper() in table else i) for i in items]


def has_tag(s, *tags):
    values = [i.upper() for i in re.split(r'[-_\s]', s)]
    for tag in tags:
        if tag.upper() in values:
            return True
    return False


def has_embedded_chinese_subtitle(video_name):
    name, ext = os.path.splitext(
        os.path.basename(video_name))
    if ext.lower() not in VIDEO_EXTENSIONS:
        return False

    return CHINESE_SUBTITLE in name or has_tag(name, 'C', 'UC', 'ch')


def has_external_chinese_subtitle(video_name, *filenames):
    if not filenames:
        if not os.path.exists(video_name):
            return False
        return has_external_chinese_subtitle(video_name, *os.listdir(os.path.dirname(video_name)))

    basename, ext = os.path.splitext(
        os.path.basename(video_name))
    if ext.lower() not in VIDEO_EXTENSIONS:
        return False

    r = re.compile(
        r'\.(chinese|ch[ist]|zh(-(cn|hk|tw|hans|hant))?)\.(ass|srt|ssa|stl|sub|vid|vtt)$', re.IGNORECASE)
    for filename in filenames:
        if r.search(filename) and r.sub('', filename).upper() == basename.upper():
            return True
    return False


def has_chinese_subtitle(video_name):
    return has_embedded_chinese_subtitle(video_name) or \
        has_external_chinese_subtitle(video_name)
