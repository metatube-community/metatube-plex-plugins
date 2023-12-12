# -*- coding: utf-8 -*-

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.locale_kit import Locale  # locale kit

# Plugin Consts
PLUGIN_NAME = 'MetaTube'
DEFAULT_USER_AGENT = '%s.bundle' % PLUGIN_NAME

# Content Rating
DEFAULT_RATING = 'JP-18+'
DEFAULT_COUNTRY = 'Japan'

# Chinese Subtitle
CHINESE_SUBTITLE = '中文字幕'

# Default Values
DEFAULT_TITLE_TEMPLATE = '{number} {title}'
DEFAULT_TAGLINE_TEMPLATE = '配信開始日 {date}'

# Supported Languages
LANGUAGES = [
    Locale.Language.Chinese,
    Locale.Language.Japanese,
    Locale.Language.Korean,
    Locale.Language.English,
    Locale.Language.Russian,
    Locale.Language.Vietnamese,
    Locale.Language.Thai,
    Locale.Language.Arabic,
    Locale.Language.French,
    Locale.Language.Finnish,
    Locale.Language.Greek,
    Locale.Language.Italian,
    Locale.Language.German,
    Locale.Language.Spanish,
    Locale.Language.Portuguese,
    Locale.Language.Danish,
    Locale.Language.Dutch,
    Locale.Language.Swedish,
]

# Preference Keys
KEY_API_SERVER = 'api_server'
KEY_API_TOKEN = 'api_token'
KEY_ENABLE_COLLECTIONS = 'enable_collections'
KEY_ENABLE_CHAPTERS = 'enable_chapters'
KEY_ENABLE_DIRECTORS = 'enable_directors'
KEY_ENABLE_RATINGS = 'enable_ratings'
KEY_ENABLE_TRAILERS = 'enable_trailers'
KEY_ENABLE_REAL_ACTOR_NAMES = 'enable_real_actor_names'
KEY_ENABLE_BADGES = 'enable_badges'
KEY_BADGE_URL = 'badge_url'
KEY_ENABLE_MOVIE_PROVIDER_FILTER = 'enable_movie_provider_filter'
KEY_MOVIE_PROVIDER_FILTER = 'movie_provider_filter'
KEY_ENABLE_TITLE_TEMPLATE = 'enable_title_template'
KEY_TITLE_TEMPLATE = 'title_template'
KEY_ENABLE_ACTOR_SUBSTITUTION = 'enable_actor_substitution'
KEY_ACTOR_SUBSTITUTION = 'actor_substitution_table'
KEY_ENABLE_GENRE_SUBSTITUTION = 'enable_genre_substitution'
KEY_GENRE_SUBSTITUTION = 'genre_substitution_table'
KEY_TRANSLATION_MODE = 'translation_mode'
KEY_TRANSLATION_ENGINE = 'translation_engine'
KEY_TRANSLATION_ENGINE_PARAMETERS = 'translation_engine_parameters'

# Translation Enums
TRANSLATION_MODE_DISABLED = 'Disabled'
TRANSLATION_MODE_TITLE = 'Title'
TRANSLATION_MODE_SUMMARY = 'Summary'
TRANSLATION_MODE_TITLE_SUMMARY = 'Title and Summary'

TRANSLATION_MODE_ENUMS = {
    TRANSLATION_MODE_DISABLED: 0b0000,
    TRANSLATION_MODE_TITLE: 0b0001,
    TRANSLATION_MODE_SUMMARY: 0b0010,
    TRANSLATION_MODE_TITLE_SUMMARY: 0b0011,
}
