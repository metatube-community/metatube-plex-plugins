# -*- coding: utf-8 -*-

from api_client import APIClient, APIError, MovieSearchResult
from constants import PLUGIN_NAME, DEFAULT_USER_AGENT, LANGUAGES
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

    def __init__(self, *args, **kwargs):
        Agent.Movies.__init__(self, *args, **kwargs)
        self.api = APIClient()

    @staticmethod
    def parse_filename(filename):
        return unquote(basename(filename))

    def search(self,
               results,  # type:
               media,  # type: Media.Movie
               lang,  # type: str
               manual=False,  # type: bool
               ):
        position = None
        search_results = []  # type: list[MovieSearchResult]
        default_query = self.parse_filename(media.filename)

        if not manual:
            search_results = self.api.search_movie(q=default_query)
        else:
            try:  # exact match by provider and id
                if not media.year or \
                        not isinstance(media.year, str):
                    raise ValueError
                pid = ProviderID.Parse(
                    media.year,  # HACK: use `year` field as pid input
                )
                position = pid.position  # update position
                search_results.append(self.api.get_movie_info(
                    pid.provider, pid.id, pid.update is not True))
            except ValueError:
                search_results = self.api.search_movie(
                    q=default_query if media.openSubtitlesHash  # auto match
                    else media.name  # with search options
                )

        # TODO: add provider filter here

        if not search_results:
            Log.Warn("Movie not found: {items}".format(items=vars(media)))
            return results

        for m in search_results:
            results.Append(MetadataSearchResult(
                id=str(ProviderID(
                    provider=m.provider,
                    id=m.id,
                    position=position)),
                name='[{provider}] {number} {title}'.format(
                    provider=m.provider,
                    number=m.number,
                    title=m.title),
                year=m.release_date.year if m.release_date.year > 1900 else None,
                score=int(m.score * 20),
                lang=Locale.Language.Japanese or lang,
                # thumb=Proxy.Remote,
            ))

        return results

    def update(self,
               metadata,  # type: MetadataItem
               media,  # type: Media.Movie
               lang,  # type: str
               force=False,  # type: bool
               ):
        pass
