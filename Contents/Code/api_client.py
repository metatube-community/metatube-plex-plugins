# -*- coding: utf-8 -*-

import requests

# import urljoin
try:  # Python 2
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.core_kit import Core  # core kit
    from plexhints.log_kit import Log  # log kit
    from plexhints.prefs_kit import Prefs  # prefs kit


class APIClient:
    _ACTOR_INFO_API = '/v1/actors'
    _MOVIE_INFO_API = '/v1/movies'
    _ACTOR_SEARCH_API = '/v1/actors/search'
    _MOVIE_SEARCH_API = '/v1/movies/search'
    _PRIMARY_IMAGE_API = '/v1/images/primary'
    _THUMB_IMAGE_API = '/v1/images/thumb'
    _BACKDROP_IMAGE_API = '/v1/images/backdrop'
    _TRANSLATE_API = '/v1/translate'

    def __init__(self):
        self.http = requests.Session()

    def _compose_url(self):
        pass

    def _get_data(self):
        pass

    def search_movie(self):
        pass

    def search_actor(self):
        pass

    def get_movie_info(self):
        pass

    def get_actor_info(self):
        pass

    def translate(self):
        pass


def test():
    pass


if __name__ == '__main__':
    test()
