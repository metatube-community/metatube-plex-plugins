# -*- coding: utf-8 -*-

try:  # Python 2
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin
finally:
    from os.path import join as pathjoin
    from constants import DEFAULT_USER_AGENT
    from requests import Session, PreparedRequest

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.prefs_kit import Prefs  # prefs kit


class APIError(Exception):
    """An API error occurred."""


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
        self.session = Session()

    def __del__(self):
        self.session.close()

    @staticmethod
    def _prepare_url(*paths, **params):
        req = PreparedRequest()
        req.prepare_url(
            url=urljoin(Prefs['metatube.server'], pathjoin(*paths)),
            params=params)
        return req.url

    def _get_data(self, url, require_auth=False):
        headers = {
            'Accept': 'application/json',
            'User-Agent': DEFAULT_USER_AGENT
        }
        if require_auth:
            headers['Authorization'] = 'Bearer %s' % Prefs['metatube.token']

        with self.session.get(url=url, headers=headers) as r:
            info = r.json()
            data = info.get('data')
            error = info.get('error')

            if error:
                raise APIError('API request error: %d <%s>' %
                               (error['code'], error['message']))
            if not data:
                raise APIError('Response data field is empty')

            return data

    def search_actor(self, q, provider=None, fallback=None):
        return self._get_data(
            url=self._prepare_url(
                self._ACTOR_SEARCH_API,
                q=q, provider=provider, fallback=fallback),
            require_auth=True)

    def search_movie(self, q, provider=None, fallback=None):
        return self._get_data(
            url=self._prepare_url(
                self._MOVIE_SEARCH_API,
                q=q, provider=provider, fallback=fallback),
            require_auth=True)

    def get_actor_info(self, provider, id, lazy=None):
        return self._get_data(
            url=self._prepare_url(
                self._ACTOR_INFO_API, provider, id,
                lazy=lazy),
            require_auth=True)

    def get_movie_info(self, provider, id, lazy=None):
        return self._get_data(
            url=self._prepare_url(
                self._MOVIE_INFO_API, provider, id,
                lazy=lazy),
            require_auth=True)

    def get_primary_image_url(self, provider, id, ratio=None, pos=None):
        return self._prepare_url(
            self._PRIMARY_IMAGE_API, provider, id,
            ratio=ratio, pos=pos)

    def get_thumb_image_url(self, provider, id):
        return self._prepare_url(
            self._THUMB_IMAGE_API, provider, id)

    def get_backdrop_image_url(self, provider, id):
        return self._prepare_url(
            self._BACKDROP_IMAGE_API, provider, id)

    def translate(self, q, to, engine, **params):
        return self._get_data(
            url=self._prepare_url(
                self._TRANSLATE_API,
                q=q, to=to, engine=engine, **params),
            require_auth=False)


api = APIClient()
