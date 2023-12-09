# -*- coding: utf-8 -*-

try:  # Python 2
    import httplib as http_status
    from urlparse import urljoin
except ImportError:  # Python 3
    from http import HTTPStatus as http_status
    from urllib.parse import urljoin
finally:
    from datetime import datetime
    from posixpath import join as pathjoin
    from requests import Session, PreparedRequest
    from constants import DEFAULT_USER_AGENT, KEY_API_SERVER, KEY_API_TOKEN

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.prefs_kit import Prefs  # prefs kit


def parse_date(dt):
    for fmt in [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ]:
        try:
            return datetime.strptime(dt, fmt)
        except ValueError:
            continue
    return datetime(year=0, month=0, day=0)


class BaseInfoObject(object):
    def __init__(self, **data):
        self.id = data['id']  # type: str
        self.provider = data['provider']  # type: str
        self.homepage = data['homepage']  # type: str


class ActorSearchResult(BaseInfoObject):
    def __init__(self, **data):
        BaseInfoObject.__init__(self, **data)
        self.name = data['name']  # type: str
        self.images = data['images']  # type: list[str]


class ActorInfoObject(ActorSearchResult):
    def __init__(self, **data):
        ActorSearchResult.__init__(self, **data)


class MovieSearchResult(BaseInfoObject):
    def __init__(self, **data):
        BaseInfoObject.__init__(self, **data)
        self.number = data['number']  # type: str
        self.title = data['title']  # type: str
        self.cover_url = data['cover_url']  # type: str
        self.thumb_url = data['thumb_url']  # type: str
        self.score = data['score']  # type: float
        self.release_date = data['release_date']  # type: datetime
        self.actors = data.get('actors', [])  # type: list[str]


class MovieInfoObject(MovieSearchResult):
    def __init__(self, **data):
        MovieSearchResult.__init__(self, **data)


class APIError(Exception):
    """An API error occurred."""


class APIClient(object):
    ACTOR_INFO_API = '/v1/actors/{0}/{1}'
    MOVIE_INFO_API = '/v1/movies/{0}/{1}'
    ACTOR_SEARCH_API = '/v1/actors/search'
    MOVIE_SEARCH_API = '/v1/movies/search'
    PRIMARY_IMAGE_API = '/v1/images/primary/{0}/{1}'
    THUMB_IMAGE_API = '/v1/images/thumb/{0}/{1}'
    BACKDROP_IMAGE_API = '/v1/images/backdrop/{0}/{1}'
    TRANSLATE_API = '/v1/translate'

    def __init__(self):
        self.session = Session()

    @staticmethod
    def prepare_url(tpl, *paths, **params):
        req = PreparedRequest()
        req.prepare_url(
            url=urljoin(Prefs[KEY_API_SERVER], tpl.format(*paths)),
            params=params)
        return req.url

    def get_JSON(self, url, require_auth=False):
        headers = {
            'Accept': 'application/json',
            'User-Agent': DEFAULT_USER_AGENT
        }
        if require_auth:
            headers['Authorization'] = 'Bearer %s' % Prefs[KEY_API_TOKEN]

        with self.session.get(url=url, headers=headers) as r:
            info = r.json()
            data = info.get('data')
            error = info.get('error')

            if r.status_code != http_status.OK and error:
                raise APIError('API request error: %d <%s>' %
                               (error['code'], error['message']))
            if not data:
                raise APIError('Response data field is empty')

            return data

    def search_actor(self, q, provider=None, fallback=None):
        return [ActorSearchResult(**data)
                for data in self.get_JSON(
                url=self.prepare_url(
                    self.ACTOR_SEARCH_API,
                    q=q, provider=provider, fallback=fallback),
                require_auth=True)]

    def search_movie(self, q, provider=None, fallback=None):
        return [MovieSearchResult(**data)
                for data in self.get_JSON(
                url=self.prepare_url(
                    self.MOVIE_SEARCH_API,
                    q=q, provider=provider, fallback=fallback),
                require_auth=True)]

    def get_actor_info(self, provider, id, lazy=None):
        return self.get_JSON(
            url=self.prepare_url(
                self.ACTOR_INFO_API, provider, id,
                lazy=lazy),
            require_auth=True)

    def get_movie_info(self, provider, id, lazy=None):
        return self.get_JSON(
            url=self.prepare_url(
                self.MOVIE_INFO_API, provider, id,
                lazy=lazy),
            require_auth=True)

    def get_primary_image_url(self, provider, id, ratio=None, pos=None):
        return self.prepare_url(
            self.PRIMARY_IMAGE_API, provider, id,
            ratio=ratio, pos=pos)

    def get_thumb_image_url(self, provider, id):
        return self.prepare_url(
            self.THUMB_IMAGE_API, provider, id)

    def get_backdrop_image_url(self, provider, id):
        return self.prepare_url(
            self.BACKDROP_IMAGE_API, provider, id)

    def translate(self, q, to, engine, **params):
        return self.get_JSON(
            url=self.prepare_url(
                self.TRANSLATE_API,
                q=q, to=to, engine=engine, **params),
            require_auth=False)


# Export API
api = APIClient()
