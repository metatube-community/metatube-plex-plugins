# -*- coding: utf-8 -*-
import threading
import time

import utils
from api_client import api
from constants import *

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.locale_kit import Locale  # locale kit
    from plexhints.log_kit import Log  # log kit
    from plexhints.prefs_kit import Prefs  # prefs kit

TRANSLATOR_LOCK = threading.Lock()


def translate_text(text, lang, fallback=None):
    with TRANSLATOR_LOCK:

        translated_text = fallback

        if not text:
            Log.Warn('Translation text is empty')
            return translated_text

        if Prefs[KEY_TRANSLATION_MODE] == TRANSLATION_MODE_DISABLED:
            Log.Warn('Translation is disabled')
            return translated_text

        if lang == Locale.Language.Japanese:
            Log.Warn('Translation not applied to Japanese')
            return translated_text

        engine = Prefs[KEY_TRANSLATION_ENGINE]
        params = utils.parse_table(Prefs[KEY_TRANSLATION_ENGINE_PARAMETERS], origin_key=True)

        forced_lang = params.pop('to', None)
        if forced_lang:
            Log.Warn('Force translation language to to {forced_lang}'
                     .format(forced_lang=forced_lang))
            lang = forced_lang

        # mandatory rps limit
        time.sleep(1.0)

        try:
            translated_text = api.translate(q=text, to=lang, engine=engine,
                                            **params).translated_text
        except Exception as e:
            Log.Warn('Translate error: {error}'.format(error=e))
        finally:
            return translated_text
