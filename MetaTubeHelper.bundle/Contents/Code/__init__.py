# -*- coding: utf-8 -*-

import threading

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.agent_kit import Agent, Media  # agent kit
    from plexhints.locale_kit import Locale  # locale kit
    from plexhints.log_kit import Log  # log kit
    from plexhints.prefs_kit import Prefs  # prefs kit
    from plexhints.object_kit import MetadataSearchResult  # object kit

try:
    from localmedia import find_subtitles
except ImportError:
    def find_subtitles(part):
        Log.Debug('Fake find_subtitles called: {file}'.format(file=part.file))


# noinspection PyMethodMayBeStatic
class MetaTubeHelper(Agent.Movies):
    name = 'MetaTube Helper'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    persist_stored_files = False
    contributes_to = ['com.plexapp.agents.metatube',
                      'com.plexapp.agents.none']

    helper_global_semaphore = threading.Semaphore(1)

    def search(self, results, media, lang):
        with self.helper_global_semaphore:
            results.Append(MetadataSearchResult(id='null', score=100))

    def update(self, metadata, media, lang):
        with self.helper_global_semaphore:

            # Look for subtitles
            if Prefs['find_subtitles']:
                for item in media.items:
                    for part in item.parts:
                        find_subtitles(part)
