# -*- coding: utf-8 -*-

from localmedia import find_local_subtitles

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.agent_kit import Agent, Media  # agent kit
    from plexhints.locale_kit import Locale  # locale kit
    from plexhints.prefs_kit import Prefs  # prefs kit
    from plexhints.object_kit import MetadataSearchResult  # object kit


# noinspection PyMethodMayBeStatic
class MetaTubeHelper(Agent.Movies):
    name = 'MetaTube Helper'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    persist_stored_files = False
    contributes_to = ['com.plexapp.agents.metatube',
                      'com.plexapp.agents.none']

    def search(self, results, media, lang):
        results.Append(MetadataSearchResult(id='null', score=100))

    def update(self, metadata, media, lang):
        # Look for subtitles
        if Prefs['find_local_subtitles']:
            for item in media.items:
                for part in item.parts:
                    find_local_subtitles(part)
