# -*- coding: utf-8 -*-

import threading
from base64 import urlsafe_b64encode
from random import choice

import utils
from api_client import api
from constants import *
from provider_id import ProviderID
from translator import translate_text

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

    # Workaround:
    # - using a semaphore to prevent DB corruption
    agent_global_semaphore = threading.Semaphore(1)

    @staticmethod
    def get_rating_image(rating):
        return 'rottentomatoes://image.rating.ripe' \
            if float(rating) >= 6.0 \
            else 'rottentomatoes://image.rating.rotten'

    @staticmethod
    def get_audience_rating_image(rating):
        return 'rottentomatoes://image.rating.upright' \
            if float(rating) >= 6.0 \
            else 'rottentomatoes://image.rating.spilled'

    @staticmethod
    def get_review_image(rating):
        return 'rottentomatoes://image.review.fresh' \
            if not rating or float(rating) >= 6.0 \
            else 'rottentomatoes://image.review.rotten'

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

    @staticmethod
    def translate_movie_info(m, lang):
        mode = Prefs[KEY_TRANSLATION_MODE]

        if TRANSLATION_MODE_ENUMS[mode] & \
                TRANSLATION_MODE_ENUMS[TRANSLATION_MODE_TITLE] and m.title:
            m.title = translate_text(m.title, lang=lang, fallback=m.title)

        if TRANSLATION_MODE_ENUMS[mode] & \
                TRANSLATION_MODE_ENUMS[TRANSLATION_MODE_SUMMARY] and m.summary:
            m.summary = translate_text(m.summary, lang=lang, fallback=m.summary)

    @staticmethod
    def translate_reviews(reviews, lang):
        mode = Prefs[KEY_TRANSLATION_MODE]

        if TRANSLATION_MODE_ENUMS[mode] & \
                TRANSLATION_MODE_ENUMS[TRANSLATION_MODE_REVIEWS]:
            for review in reviews:
                if review.comment:
                    review.comment = translate_text(review.comment, lang=lang,
                                                    fallback=review.comment)

    def search(self, results, media, lang, manual=False):
        with self.agent_global_semaphore:
            return self.search_media(results, media, lang, manual)

    # noinspection PyMethodMayBeStatic
    def search_media(self, results, media, lang, manual=False):

        position = None
        search_results = []

        # issued by scanning or auto match
        if (not manual or media.openSubtitlesHash) \
                and media.filename:
            search_results = api.search_movie(
                q=utils.parse_filename_without_ext(media.filename))
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
                    provider=pid.provider, id=pid.id, lazy=(pid.update is not True)))
            except ValueError:  # fallback to name based search
                search_results = api.search_movie(q=media.name)

        # apply movie provider filter
        if Prefs[KEY_ENABLE_MOVIE_PROVIDER_FILTER]:
            movie_provider_filter = utils.parse_list(Prefs[KEY_MOVIE_PROVIDER_FILTER])
            if movie_provider_filter:
                search_results = [i for i in search_results
                                  if i.provider.upper() in movie_provider_filter]
                search_results.sort(key=lambda i: movie_provider_filter.index(i.provider.upper()))
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
                lang=lang,  # user preferred language
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

    def update(self, metadata, media, lang, force=False):
        with self.agent_global_semaphore:
            return self.update_media(metadata, media, lang, force)

    def update_media(self, metadata, media, lang, force=False):

        if force:
            Log.Debug('Force metadata refreshing')

        pid = ProviderID.Parse(metadata.id)
        Log.Info('Get movie info: {0:s}'.format(pid))

        # API Request
        m = api.get_movie_info(provider=pid.provider, id=pid.id)

        original_title = m.title
        release_date = m.release_date.strftime('%Y-%m-%d')

        # Detect Chinese Subtitles
        chinese_subtitle_on = False
        for filename in (p.file for p in utils.extra_media_parts(media)):
            if utils.has_chinese_subtitle(filename):
                chinese_subtitle_on = True
                m.genres.append(CHINESE_SUBTITLE)
                Log.Debug('Chinese subtitle detected for {filename}'
                          .format(filename=filename))
                break

        # Apply Preferences
        if Prefs[KEY_ENABLE_REAL_ACTOR_NAMES]:
            self.convert_to_real_actor_names(m)

        if Prefs[KEY_ENABLE_ACTOR_SUBSTITUTION] and Prefs[KEY_ACTOR_SUBSTITUTION]:
            m.actors = utils.table_substitute(
                utils.parse_table(Prefs[KEY_ACTOR_SUBSTITUTION],
                                  sep='\n', b64=True), m.actors)

        if Prefs[KEY_ENABLE_GENRE_SUBSTITUTION] and Prefs[KEY_GENRE_SUBSTITUTION]:
            m.genres = utils.table_substitute(
                utils.parse_table(Prefs[KEY_GENRE_SUBSTITUTION],
                                  sep='\n', b64=True), m.genres)

        # Translate Info
        if Prefs[KEY_TRANSLATION_MODE] != TRANSLATION_MODE_DISABLED:
            self.translate_movie_info(m, lang=lang)

        # Title
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
            date=release_date,
        )

        # Basic Metadata
        metadata.summary = m.summary
        metadata.original_title = original_title

        # Set pid to tagline field
        metadata.tagline = '{pid:s}'.format(pid=pid)

        # Content Rating
        metadata.content_rating = DEFAULT_RATING

        # Producing Country
        metadata.countries.clear()
        metadata.countries.add(DEFAULT_COUNTRY)

        # Studio
        if m.maker.strip():
            metadata.studio = m.maker

        # Release Date
        if m.release_date.year > 1900:
            metadata.originally_available_at = m.release_date
            metadata.year = m.release_date.year

        # Duration
        if m.runtime:
            metadata.duration = m.runtime * 60 * 1000  # millisecond

        # Clear Ratings
        metadata.rating = 0.0
        metadata.audience_rating = 0.0
        metadata.rating_image = None
        metadata.audience_rating_image = None
        # Clear Reviews
        metadata.reviews.clear()
        # Ratings & Reviews
        if Prefs[KEY_ENABLE_RATINGS] and m.score:
            metadata.rating = m.score * 2.0
            metadata.rating_image = self.get_rating_image(metadata.rating)

            if Prefs[KEY_ENABLE_REVIEWS]:
                try:
                    reviews = api.get_movie_reviews(m.provider, m.id, homepage=m.homepage)
                except Exception as e:
                    Log.Warn('Get reviews for {id} failed {error}'.format(id=m.id, error=e))
                else:
                    if Prefs[KEY_TRANSLATION_MODE] != TRANSLATION_MODE_DISABLED:
                        self.translate_reviews(reviews, lang=lang)
                    for review in reviews:
                        r = metadata.reviews.new()
                        r.author = review.author
                        r.source = m.provider
                        r.image = self.get_review_image(review.score * 2)
                        r.link = m.homepage
                        r.text = review.comment
                        _ = review.title  # title is never used

                    # Audience Rating
                    scores = [i.score for i in reviews if i.score > 0]
                    metadata.audience_rating = utils.average(scores) * 2
                    metadata.audience_rating_image = self.get_audience_rating_image(metadata.audience_rating)

        # Director
        metadata.directors.clear()
        if Prefs[KEY_ENABLE_DIRECTORS] and m.director:
            director = metadata.directors.new()
            director.name = m.director
            metadata.directors.add(director)

        # Collections
        metadata.collections.clear()
        if Prefs[KEY_ENABLE_COLLECTIONS] and m.series.strip():
            metadata.collections.add(m.series)

        # Genres
        metadata.genres.clear()
        for genre in set(m.genres):
            metadata.genres.add(genre)

        # Tags
        metadata.tags.clear()
        for tag in {m.maker, m.series, m.label}:
            if tag.strip():
                metadata.tags.add(tag)

        # Actors
        metadata.roles.clear()
        for actor in set(m.actors):
            role = metadata.roles.new()
            role.name = actor
            role.photo = self.get_actor_image_url(name=actor)

        # CHS Badge
        badge = Prefs[KEY_BADGE_URL] \
            if Prefs[KEY_ENABLE_BADGES] and chinese_subtitle_on else None

        # Poster Image
        primary = api.get_primary_image_url(m.provider, m.id, pos=pid.position, badge=badge)
        # noinspection PyBroadException
        try:
            metadata.posters[primary] = Proxy.Media(api.get_content(url=primary))
        except:
            Log.Warn('Failed to load poster image: {primary}'.format(primary=primary))

        # Art Image
        backdrop = api.get_backdrop_image_url(m.provider, m.id)
        # noinspection PyBroadException
        try:
            metadata.art[backdrop] = Proxy.Media(api.get_content(url=backdrop))
        except:
            Log.Warn('Failed to load art image: {backdrop}'.format(backdrop=backdrop))

        # Trailer
        trailer_url = (m.preview_video_url or
                       m.preview_video_hls_url)

        if Prefs[KEY_ENABLE_TRAILERS] and trailer_url:
            # Choose thumb for trailer
            if m.preview_images:
                thumb = api.get_thumb_image_url(m.provider, m.id,
                                                url=choice(m.preview_images))
            else:
                thumb = api.get_thumb_image_url(m.provider, m.id)

            trailer = TrailerObject(
                url='{plugin}://trailer/{b64url}'.format(
                    plugin=PLUGIN_NAME.lower(),
                    b64url=urlsafe_b64encode(trailer_url)
                ),
                title='Trailer: {number}'.format(number=m.number),
                thumb=thumb,
            )
            metadata.extras.add(trailer)
            Log.Debug('Trailer added: {trailer}'.format(trailer=trailer_url))

        return metadata
