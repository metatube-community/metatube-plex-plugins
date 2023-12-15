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

# Chinese Subtitle
CHINESE_SUBTITLE = '中文字幕'

# Content Rating
DEFAULT_RATING = 'JP-18+'
DEFAULT_COUNTRY = 'Japan'

# Default Template
DEFAULT_TITLE_TEMPLATE = '{number} {title}'
DEFAULT_TRAILER_TEMPLATE = 'サンプル動画 {original_title}'

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

# File Extensions
SUBTITLE_EXTENSIONS = ('.utf', '.utf8', '.utf-8', '.srt', '.smi',
                       '.rt', '.ssa', '.aqt', '.jss', '.ass',
                       '.idx', '.sub', '.txt', '.psb', '.vtt')
VIDEO_EXTENSIONS = ('.3g2', '.3gp', '.asf', '.asx', '.avc', '.avi',
                    '.avs', '.bivx', '.bup', '.divx', '.dv', '.dvr-ms',
                    '.evo', '.fli', '.flv', '.m2t', '.m2ts', '.m2v',
                    '.m4v', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg',
                    '.mts', '.nsv', '.nuv', '.ogm', '.ogv', '.tp',
                    '.pva', '.qt', '.rm', '.rmvb', '.sdp', '.svq3',
                    '.strm', '.ts', '.ty', '.vdr', '.viv', '.vob',
                    '.vp3', '.wmv', '.wpl', '.wtv', '.xsp', '.xvid', '.webm')

# Preference Keys
KEY_API_SERVER = 'api_server'
KEY_API_TOKEN = 'api_token'
KEY_FIND_SUBTITLES = 'find_subtitles'
KEY_ENABLE_COLLECTIONS = 'enable_collections'
KEY_ENABLE_DIRECTORS = 'enable_directors'
KEY_ENABLE_RATINGS = 'enable_ratings'
KEY_ENABLE_REVIEWS = 'enable_reviews'
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
TRANSLATION_MODE_REVIEWS = 'Reviews'
TRANSLATION_MODE_TITLE_SUMMARY = 'Title and Summary'
TRANSLATION_MODE_TITLE_SUMMARY_REVIEWS = 'Title, Summary and Reviews'

TRANSLATION_MODE_ENUMS = {
    TRANSLATION_MODE_DISABLED: 0b0000,
    TRANSLATION_MODE_TITLE: 0b0001,
    TRANSLATION_MODE_SUMMARY: 0b0010,
    TRANSLATION_MODE_REVIEWS: 0b0100,
    TRANSLATION_MODE_TITLE_SUMMARY: 0b0011,
    TRANSLATION_MODE_TITLE_SUMMARY_REVIEWS: 0b0111,
}
