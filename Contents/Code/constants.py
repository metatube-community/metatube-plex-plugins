# -*- coding: utf-8 -*-

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.locale_kit import Locale  # locale kit

# Common Languages
LANGUAGES = [
    Locale.Language.Chinese,
    Locale.Language.Japanese,
    Locale.Language.Korean,
    Locale.Language.English,
    Locale.Language.Russian,
]

# Content Rating
DEFAULT_RATING = 'JP-18+'

# Plugin Consts
PLUGIN_NAME = 'MetaTube'
DEFAULT_USER_AGENT = '%s.bundle' % PLUGIN_NAME

# Preference Keys
KEY_API_SERVER = 'api_server'
KEY_API_TOKEN = 'api_token'
KEY_ENABLE_DIRECTORS = 'enable_directors'
KEY_ENABLE_RATINGS = 'enable_ratings'
KEY_ENABLE_TRAILERS = 'enable_trailers'
KEY_ENABLE_REAL_ACTOR_NAMES = 'enable_real_actor_names'
