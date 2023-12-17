# -*- coding: utf-8 -*-
import os
import re
import sys
from base64 import b64decode
from datetime import datetime

from constants import *

try:  # Python 2
    from urllib import unquote
except ImportError:  # Python 3
    from urllib.parse import unquote

# Python 3 compatible code
if sys.version_info.major == 3:
    unicode = str
    # noinspection PyShadowingBuiltins
    filter = lambda f, t: u''.join(i for i in t if f(i))


# Based on an answer by John Machin on Stack Overflow:
# - http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
def filter_invalid_xml_chars(s):
    def is_valid_xml_char(i):
        c = ord(i)
        return (0x20 <= c <= 0xD7FF or
                0xE000 <= c <= 0xFFFD or
                0x10000 <= c <= 0x10FFFF or
                c in (0x9, 0xA, 0xD))

    return filter(is_valid_xml_char, s)


def safe_unicode(o):
    if isinstance(o, unicode):
        return filter_invalid_xml_chars(o)
    elif isinstance(o, list):
        return [safe_unicode(v) for v in o]
    elif isinstance(o, dict):
        return dict((k, safe_unicode(v)) for k, v in o.items())
    else:
        return o


def average(a):
    x = 0.0
    if not a:
        return x
    for i in a:
        x = x + i
    return x / len(a)


def parse_filename(filename):
    return os.path.basename(unquote(filename))


def parse_filename_without_ext(filename):
    return os.path.splitext(parse_filename(filename))[0]


def parse_date(s):
    # noinspection PyBroadException
    try:
        return datetime.strptime(
            re.findall(r'\d{4}-\d{2}-\d{2}', s)[0], '%Y-%m-%d')
    except:
        return datetime(1, 1, 1)  # default value


def parse_list(s, sep=','):
    return [i.strip().upper() for i in s.split(sep) if i.strip()]


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


def has_embedded_chinese_subtitle(video_name):
    def has_tag(s, *tags):
        values = [i.upper() for i in re.split(r'[-_\s]', s)]
        for tag in tags:
            if tag.upper() in values:
                return True
        return False

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
        r'\.(ch[ist]|zho?(-(cn|hk|sg|tw))?)\.(ass|srt|ssa|smi|sub|idx|psb|vtt)$', re.IGNORECASE)
    for filename in filenames:
        if r.search(filename) and r.sub('', filename).upper() == basename.upper():
            return True
    return False


def has_chinese_subtitle(video_name):
    return has_embedded_chinese_subtitle(video_name) or \
        has_external_chinese_subtitle(video_name)


def extra_media_parts(obj):
    if not hasattr(obj, 'all_parts'):
        return ()
    return [part for part in obj.all_parts()
            if hasattr(part, 'file') and hasattr(part, 'duration')]


def extra_media_durations(obj):
    parts = extra_media_parts(obj)

    # single file version
    if len(parts) == 1:
        return {parts[0].file: int(parts[0].duration)}

    # multi-disk file match
    r = re.compile(r'-\s*(cd|disc|disk|dvd|pt|part)(\d+)$', re.IGNORECASE)

    durations = {}
    for part in parts:
        if int(part.duration) > 0:
            name, ext = os.path.splitext(part.file)

            if r.search(name):
                key = re.sub(r'\d+$', '', name) + ext
            else:
                key = name + ext

            durations.setdefault(key, 0)
            durations[key] = durations[key] + int(part.duration)

    return durations
