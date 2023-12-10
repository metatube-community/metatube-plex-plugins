# -*- coding: utf-8 -*-

from api_client import api, APIError, MovieSearchResult
from constants import PLUGIN_NAME, DEFAULT_USER_AGENT, DEFAULT_RATING, \
    DEFAULT_TITLE_TEMPLATE, CHINESE_SUBTITLE, LANGUAGES, \
    KEY_ENABLE_COLLECTIONS, KEY_ENABLE_DIRECTORS, KEY_ENABLE_RATINGS, KEY_ENABLE_TRAILERS, \
    KEY_ENABLE_REAL_ACTOR_NAMES, KEY_ENABLE_BADGES, KEY_BADGE_URL, KEY_ENABLE_MOVIE_PROVIDER_FILTER, \
    KEY_MOVIE_PROVIDER_FILTER, KEY_ENABLE_TITLE_TEMPLATE, KEY_TITLE_TEMPLATE, KEY_ENABLE_ACTOR_SUBSTITUTION, \
    KEY_ACTOR_SUBSTITUTION, KEY_ENABLE_GENRE_SUBSTITUTION, KEY_GENRE_SUBSTITUTION
from provider_id import ProviderID
from utils import parse_table, table_substitute, has_chinese_subtitle

try:  # Python 2
    from urllib import unquote
except ImportError:  # Python 3
    from urllib.parse import unquote
finally:
    from os.path import basename

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.agent_kit import Agent, Media  # agent kit
    from plexhints.core_kit import Core  # core kit
    from plexhints.decorator_kit import handler, indirect, route  # decorator kit
    from plexhints.exception_kit import Ex  # exception kit
    from plexhints.locale_kit import Locale  # locale kit
    from plexhints.log_kit import Log  # log kit
    from plexhints.model_kit import Movie, VideoClip, VideoClipObject  # model kit
    from plexhints.network_kit import HTTP  # network kit
    from plexhints.object_kit import Callback, IndirectResponse, MediaObject, MessageContainer, MetadataItem, \
        MetadataSearchResult, PartObject, SearchResult  # object kit
    from plexhints.parse_kit import HTML, JSON, Plist, RSS, XML, YAML  # parse kit
    from plexhints.prefs_kit import Prefs  # prefs kit
    from plexhints.proxy_kit import Proxy  # proxy kit
    from plexhints.resource_kit import Resource  # resource kit
    from plexhints.shortcut_kit import L, E, D, R, S  # shortcut kit
    from plexhints.util_kit import String, Util  # util kit

    from plexhints.constant_kit import CACHE_1MINUTE, CACHE_1HOUR, CACHE_1DAY, CACHE_1WEEK, CACHE_1MONTH  # constant kit
    from plexhints.constant_kit import ClientPlatforms, Protocols, OldProtocols, ServerPlatforms, ViewTypes, \
        SummaryTextTypes, AudioCodecs, VideoCodecs, Containers, ContainerContents, \
        StreamTypes  # constant kit, more commonly used in URL services

    # extra objects
    from plexhints.extras_kit import BehindTheScenesObject, ConcertVideoObject, DeletedSceneObject, FeaturetteObject, \
        InterviewObject, LiveMusicVideoObject, LyricMusicVideoObject, MusicVideoObject, OtherObject, \
        SceneOrSampleObject, ShortObject, TrailerObject


def Start():
    HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1DAY
    HTTP.Headers['Accept-Encoding'] = 'gzip'
    HTTP.Headers['User-Agent'] = DEFAULT_USER_AGENT


def ValidatePrefs():
    Log.Debug('ValidatePrefs called.')


class MetaTubeAgent(Agent.Movies):
    name = PLUGIN_NAME
    languages = LANGUAGES
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia',
                    'com.plexapp.agents.lambda',
                    'com.plexapp.agents.xbmcnfo']
    contributes_to = ['com.plexapp.agents.none']

    def __init__(self, *args, **kwargs):
        super(MetaTubeAgent, self).__init__(*args, **kwargs)

        self.movie_provider_filter = [i.upper() for i in Prefs[KEY_MOVIE_PROVIDER_FILTER].split(',')] \
            if Prefs[KEY_ENABLE_MOVIE_PROVIDER_FILTER] else []

        self.actor_substitution_table = parse_table(Prefs[KEY_ACTOR_SUBSTITUTION]) \
            if Prefs[KEY_ENABLE_ACTOR_SUBSTITUTION] else {}

        self.genre_substitution_table = parse_table(Prefs[KEY_GENRE_SUBSTITUTION]) \
            if Prefs[KEY_ENABLE_GENRE_SUBSTITUTION] else {}

    @staticmethod
    def parse_filename(filename):
        return basename(unquote(filename))

    @staticmethod
    def get_actor_image_url(name):

        G_FRIENDS = 'GFriends'

        try:
            for actor in api.search_actor(q=name, provider=G_FRIENDS, fallback=False):
                if actor.images:
                    return api.get_primary_image_url(provider=G_FRIENDS, id=name,
                                                     url=actor.images[0], ratio=1.0, auto=True)
        except Exception as e:
            Log.Warn('Get actor image error: {name} ({error})'.format(name=name, error=e))

    @staticmethod
    def convert_to_real_actor_names(m):

        AV_BASE_SUPPORTED_PROVIDERS = (
            'DUGA',
            'FANZA',
            'GETCHU',
            'MGS',
            'PCOLLE'
        )
        if m.provider.upper() not in AV_BASE_SUPPORTED_PROVIDERS:
            return

        AV_BASE = 'AvBase'

        try:
            results = api.search_movie(q=m.id, provider=AV_BASE)
            if not results:
                Log.Warn('Movie not found on AVBASE: {id}'.format(id=m.id))
            elif len(results) > 1:
                Log.Warn('Multiple movies found on AVBASE: {id}'.format(id=m.id))
            elif results[0].actors:
                m.actors = results[0].actors
        except Exception as e:
            Log.Warn('Convert to real actor names error: {number} ({error})'.format(number=m.number, error=e))

    def search(self,
               results,  # type: SearchResult
               media,  # type: Media.Movie
               lang,  # type: str
               manual=False,  # type: bool
               ):

        # ignore unused lang param
        _ = lang

        position = None
        search_results = []  # type: list[MovieSearchResult]

        # issued by scanning or auto match
        if (not manual or media.openSubtitlesHash) \
                and media.filename:
            search_results = api.search_movie(
                q=self.parse_filename(media.filename))
        else:
            try:  # exact match by provider and id
                if not media.year or \
                        not isinstance(media.year, str):
                    raise ValueError
                pid = ProviderID.Parse(
                    media.year,  # HACK: use `year` field as pid input
                )
                position = pid.position  # update position
                search_results.append(api.get_movie_info(
                    pid.provider, pid.id, pid.update is not True))
            except ValueError:  # fallback to name based search
                search_results = api.search_movie(q=media.name)

        # apply movie provider filter
        if Prefs[KEY_ENABLE_MOVIE_PROVIDER_FILTER]:
            if self.movie_provider_filter:
                search_results = [i for i in search_results
                                  if i.provider.upper() in self.movie_provider_filter]
                search_results.sort(key=lambda i: self.movie_provider_filter.index(i.provider.upper()))
            else:
                Log.Warn('Movie provider filter enabled but never used')

        if not search_results:
            Log.Warn('Movie not found: {items}'.format(items=vars(media)))
            return results

        for i, m in enumerate(search_results):
            pid = str(ProviderID(
                provider=m.provider,
                id=m.id,
                position=position,
            ))
            search_result = MetadataSearchResult(
                id=pid,
                name=pid,
                year=(m.release_date.year
                      if m.release_date.year > 1900 else None),
                score=int(100 - i),
                lang=Locale.Language.Japanese,
                thumb=api.get_primary_image_url(
                    m.provider, m.id,
                    url=m.thumb_url,
                    pos=1.0, auto=True),
            )
            # HACK: force to add type and summary
            search_result.type = 'movie'
            search_result.summary = DEFAULT_TITLE_TEMPLATE \
                .format(number=m.number, title=m.title)
            results.Append(search_result)

        return results

    def update(self,
               metadata,  # type: Movie
               media,  # type: Media.Movie
               lang,  # type: str
               force=False,  # type: bool
               ):

        pid = ProviderID.Parse(metadata.id)

        Log.Info('Get movie info: {0:s}'.format(pid))

        # API Request:
        m = api.get_movie_info(provider=pid.provider, id=pid.id)

        original_title = m.title

        # Chinese Subtitle:
        chinese_subtitle_on = False
        if media.filename and has_chinese_subtitle(unquote(media.filename)):
            chinese_subtitle_on = True
            m.genres.append(CHINESE_SUBTITLE)

        # Apply Preferences:
        if Prefs[KEY_ENABLE_REAL_ACTOR_NAMES]:
            self.convert_to_real_actor_names(m)

        if Prefs[KEY_ENABLE_ACTOR_SUBSTITUTION]:
            m.actors = table_substitute(self.actor_substitution_table, m.actors)

        if Prefs[KEY_ENABLE_GENRE_SUBSTITUTION]:
            m.genres = table_substitute(self.genre_substitution_table, m.genres)

        # TODO: Translate Here

        # Title:
        metadata.title = (Prefs[KEY_TITLE_TEMPLATE]
                          if Prefs[KEY_ENABLE_TITLE_TEMPLATE]
                          else DEFAULT_TITLE_TEMPLATE).format(
            provider=m.provider,
            id=m.id,
            number=m.number,
            title=m.title,
            series=m.series,
            maker=m.maker,
            label=m.label,
            director=m.director,
            actors=(' '.join(m.actors)),
            first_actor=(m.actors[0] if m.actors else ''),
            year=m.release_date.year,
            date=m.release_date.strftime('%Y-%m-%d'),
        )

        # Basic Metadata:
        metadata.summary = m.summary
        metadata.original_title = original_title

        # Content Rating:
        metadata.content_rating = DEFAULT_RATING

        # Studio:
        if m.maker.strip():
            metadata.studio = m.maker

        # Release Date:
        if m.release_date.year > 1900:
            metadata.originally_available_at = m.release_date
            metadata.year = m.release_date.year

        # Duration:
        if m.runtime:
            metadata.duration = m.runtime * 60 * 1000  # millisecond

        # Rating Score:
        if Prefs[KEY_ENABLE_RATINGS] and m.score:
            metadata.rating = m.score * 2.0
            metadata.rating_image = None
            metadata.audience_rating = 0.0
            metadata.audience_rating_image = None

        # Director:
        metadata.directors.clear()
        if Prefs[KEY_ENABLE_DIRECTORS] and m.director:
            director = metadata.directors.new()
            director.name = m.director
            metadata.directors.add(director)

        # Collections:
        metadata.collections.clear()
        if Prefs[KEY_ENABLE_COLLECTIONS] and m.series.strip():
            metadata.collections.add(m.series)

        # Genres:
        metadata.genres.clear()
        for genre in set(m.genres):
            metadata.genres.add(genre)

        # Tags:
        metadata.tags.clear()
        for tag in {m.maker, m.series, m.label}:
            if tag.strip():
                metadata.tags.add(tag)

        # Actors:
        metadata.roles.clear()
        for actor in set(m.actors):
            role = metadata.roles.new()
            role.name = actor
            role.photo = self.get_actor_image_url(name=actor)

        # CHS Badge:
        badge = Prefs[KEY_BADGE_URL] \
            if Prefs[KEY_ENABLE_BADGES] and chinese_subtitle_on else None

        # Poster Image:
        primary = api.get_primary_image_url(m.provider, m.id, pos=pid.position, badge=badge)
        # noinspection PyBroadException
        try:
            metadata.posters[primary] = Proxy.Media(api.get_content(url=primary))
        except:
            Log.Warn('Failed to load poster image: {primary}'.format(primary=primary))

        # Art Image:
        backdrop = api.get_backdrop_image_url(m.provider, m.id)
        # noinspection PyBroadException
        try:
            metadata.art[backdrop] = Proxy.Media(api.get_content(url=backdrop))
        except:
            Log.Warn('Failed to load art image: {backdrop}'.format(backdrop=backdrop))

        # Trailer:
        # if Prefs[KEY_ENABLE_TRAILERS] and trailer_url:
        #     trailer = TrailerObject(
        #         # url='{plugin}://trailer/{b64url}'.format(
        #         #     plugin=PLUGIN_NAME.lower(),
        #         #     b64url=base64.urlsafe_b64encode(trailer_url)
        #         # ),
        #         url=trailer_url,
        #         title='Trailer'
        #     )
        #     metadata.extras.add(trailer)

        return metadata
