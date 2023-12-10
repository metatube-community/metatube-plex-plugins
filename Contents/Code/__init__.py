# -*- coding: utf-8 -*-

from api_client import api, APIError, MovieSearchResult
from constants import PLUGIN_NAME, DEFAULT_USER_AGENT, LANGUAGES, \
    KEY_ENABLE_DIRECTORS, KEY_ENABLE_RATINGS, KEY_ENABLE_TRAILERS
from provider_id import ProviderID

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

    @staticmethod
    def parse_filename(filename):
        return basename(unquote(filename))

    def search(self,
               results,  # type:
               media,  # type: Media.Movie
               lang,  # type: str
               manual=False,  # type: bool
               ):
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

        # TODO: add provider filter here

        if not search_results:
            Log.Warn('Movie not found: {items}'.format(items=vars(media)))
            return results

        for i, m in enumerate(search_results):
            results.Append(MetadataSearchResult(
                id=str(ProviderID(
                    provider=m.provider,
                    id=m.id,
                    position=position)),
                name='[{provider}] {number} {title}'.format(
                    provider=m.provider,
                    number=m.number,
                    title=m.title),
                year=(m.release_date.year
                      if m.release_date.year > 1900 else None),
                score=int(100 - i),
                lang=Locale.Language.Japanese or lang,
                thumb=api.get_primary_image_url(
                    m.provider, m.id,
                    url=m.thumb_url,
                    pos=1.0, auto=True),
            ))

        return results

    def update(self,
               metadata,  # type: Movie
               media,  # type: Media.Movie
               lang,  # type: str
               force=False,  # type: bool
               ):

        pid = ProviderID.Parse(metadata.id)

        Log.Info('Get movie info: {0:s}'.format(pid))

        m = api.get_movie_info(provider=pid.provider, id=pid.id)

        original_title = m.title

        metadata.title = '{number} {title}'.format(
            number=m.number,
            title=m.title)

        if Prefs[KEY_ENABLE_RATINGS]:
            pass

        if Prefs[KEY_ENABLE_DIRECTORS]:
            pass

        if Prefs[KEY_ENABLE_TRAILERS]:
            pass

        metadata.genres = m.genres

        metadata.summary = m.summary

        metadata.studio = m.maker

        # Poster Image:
        primary = api.get_primary_image_url(m.provider, m.id, pos=pid.position)
        # noinspection PyBroadException
        try:
            metadata.posters[primary] = Proxy.Media(api.get_DATA(url=primary))
        except:
            Log.Warn('Failed to load poster image: {primary}'.format(primary=primary))

        # Art Image:
        backdrop = api.get_backdrop_image_url(m.provider, m.id)
        # noinspection PyBroadException
        try:
            metadata.art[backdrop] = Proxy.Media(api.get_DATA(url=backdrop))
        except:
            Log.Warn('Failed to load art image: {backdrop}'.format(backdrop=backdrop))

        return metadata
