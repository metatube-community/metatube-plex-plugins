# -*- coding: utf-8 -*-
#
# Code modified from: LocalMedia.bundle
#

import os
import re
import sys
import unicodedata

# plex debugging
try:
    import plexhints  # noqa: F401
except ImportError:
    pass
else:  # the code is running outside of Plex
    from plexhints.core_kit import Core  # core kit
    from plexhints.locale_kit import Locale  # locale kit
    from plexhints.log_kit import Log  # log kit
    from plexhints.proxy_kit import Proxy  # proxy kit

# Python 3 compatible code
if sys.version_info.major == 3:
    unichr = chr
    unicode = str

# Unicode control characters can appear in ID3v2 tags but are not legal in XML.
# noinspection PyUnboundLocalVariable
RE_UNICODE_CONTROL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                     u'|' + \
                     u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                     (
                         unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
                         unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
                         unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff)
                     )

SUBTITLE_EXTS = ['utf', 'utf8', 'utf-8', 'srt', 'smi', 'rt', 'ssa', 'aqt', 'jss', 'ass', 'idx', 'sub', 'txt', 'psb',
                 'vtt']
VIDEO_EXTS = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli',
              'flv',
              'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nsv', 'nuv', 'ogm', 'ogv', 'tp',
              'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv', 'wpl',
              'wtv', 'xsp', 'xvid', 'webm']


# noinspection PyBroadException
def unicodize(s):
    encoding_options = ['utf-8', sys.getdefaultencoding(), sys.getfilesystemencoding(), 'ISO-8859-1']
    normalized = False
    for encoding in encoding_options:
        try:
            s = unicodedata.normalize('NFC', unicode(s.decode(encoding)))
            normalized = True
            break
        except:
            pass

    if not normalized:
        try:
            s = unicodedata.normalize('NFC', s)
        except Exception as e:
            Log(type(e).__name__ + ' exception precomposing: ' + str(e))

    try:
        s = re.sub(RE_UNICODE_CONTROL, '', s)
    except:
        Log("Couldn't strip control characters: " + s)

    return s


def find_subtitles(part):
    RE_METAFILES = re.compile(r'^[.~]')

    lang_sub_map = {}
    part_filename = unicodize(part.file)
    part_basename = os.path.splitext(os.path.basename(part_filename))[0]
    paths = [os.path.dirname(part_filename)]

    # Check for a global subtitle location
    global_subtitle_folder = os.path.join(Core.app_support_path, 'Subtitles')
    if os.path.exists(global_subtitle_folder):
        paths.append(global_subtitle_folder)

    # We start by building a dictionary of files to their absolute paths. We also need to know
    # the number of media files that are actually present, in case the found local media asset
    # is limited to a single instance per media file.
    #
    file_paths = {}
    total_media_files = 0
    for path in paths:
        path = unicodize(path)
        for file_path_listing in os.listdir(path):

            # When using os.listdir with a unicode path, it will always return a string using the
            # NFD form. However, we internally are using the form NFC and therefore need to convert
            # it to allow correct regex / comparisons to be performed.
            #
            file_path_listing = unicodize(file_path_listing)
            if os.path.isfile(os.path.join(path, file_path_listing)) and not RE_METAFILES.search(file_path_listing):
                file_paths[file_path_listing.lower()] = os.path.join(path, file_path_listing)

            # If we've found an actual media file, we should record it.
            (root, ext) = os.path.splitext(file_path_listing)
            if ext.lower()[1:] in VIDEO_EXTS:
                total_media_files += 1

    Log('Looking for subtitle media in %d paths with %d media files.', len(paths), total_media_files)
    Log('Paths: %s', ", ".join([unicodize(p) for p in paths]))

    for file_path in file_paths.values():

        local_basename = unicodize(os.path.splitext(os.path.basename(file_path))[0])  # no language, no flag
        local_basename2 = local_basename.rsplit('.', 1)[0]  # includes language, no flag
        local_basename3 = local_basename2.rsplit('.', 1)[0]  # includes language and flag
        filename_matches_part = (local_basename == part_basename or
                                 local_basename2 == part_basename or
                                 local_basename3 == part_basename)

        # If the file is located within the global subtitle folder, and it's name doesn't match exactly
        # then we should simply ignore it.
        #
        if file_path.count(global_subtitle_folder) and not filename_matches_part:
            continue

        # If we have more than one media file within the folder and located filename doesn't match
        # exactly then we should simply ignore it.
        #
        if total_media_files > 1 and not filename_matches_part:
            continue

        subtitle_helper = SubtitleHelpers(file_path)
        if subtitle_helper is not None:
            local_lang_map = subtitle_helper.process_subtitles(part)
            for new_language, subtitles in local_lang_map.items():

                # Add the possible new language along with the located subtitles so that we can validate them
                # at the end...
                #
                if not lang_sub_map.has_key(new_language):
                    lang_sub_map[new_language] = []
                lang_sub_map[new_language] = lang_sub_map[new_language] + subtitles

    # Now whack subtitles that don't exist anymore.
    for language in lang_sub_map.keys():
        part.subtitles[language].validate_keys(lang_sub_map[language])

    # Now whack the languages that don't exist anymore.
    for language in list(set(part.subtitles.keys()) - set(lang_sub_map.keys())):
        part.subtitles[language].validate_keys({})


def SubtitleHelpers(filename):
    filename = unicodize(filename)
    for cls in [VobSubSubtitleHelper, DefaultSubtitleHelper]:
        if cls.is_helper_for(filename):
            return cls(filename)
    return None


class SubtitleHelper(object):
    def __init__(self, filename):
        self.filename = filename


class VobSubSubtitleHelper(SubtitleHelper):
    @classmethod
    def is_helper_for(cls, filename):
        (file_name, file_ext) = os.path.splitext(filename)

        # We only support idx (and maybe sub)
        if not file_ext.lower() in ['.idx', '.sub']:
            return False

        # If we've been given a sub, we only support it if there exists a matching idx file
        return os.path.exists(file_name + '.idx')

    def process_subtitles(self, part):

        lang_sub_map = {}

        # We don't directly process the sub file, only the idx. Therefore if we are passed on of these files, we simply
        # ignore it.
        (file_name, file_ext) = os.path.splitext(self.filename)
        if file_ext == '.sub':
            return lang_sub_map

        # If we have an idx file, we need to confirm there is an identically names sub file before we can proceed.
        sub_filename = file_name + ".sub"
        if not os.path.exists(sub_filename):
            return lang_sub_map

        Log('Attempting to parse VobSub file: ' + self.filename)
        idx = Core.storage.load(os.path.join(self.filename))
        if idx.count('VobSub index file') == 0:
            Log('The idx file does not appear to be a VobSub, skipping...')
            return lang_sub_map

        forced = ''
        default = ''
        split_tag = file_name.rsplit('.', 1)
        if len(split_tag) > 1 and split_tag[1].lower() in ['forced', 'default']:
            if 'forced' == split_tag[1].lower():
                forced = '1'
            if 'default' == split_tag[1].lower():
                default = '1'

        languages = {}
        language_index = 0
        basename = os.path.basename(self.filename)
        for language in re.findall('\nid: ([A-Za-z]{2})', idx):

            if not languages.has_key(language):
                languages[language] = []

            Log('Found .idx subtitle file: ' + self.filename + ' language: ' + language + ' stream index: ' + str(
                language_index) + ' default: ' + default + ' forced: ' + forced)
            languages[language].append(
                Proxy.LocalFile(self.filename, index=str(language_index), format="vobsub", default=default,
                                forced=forced))
            language_index += 1

            if not lang_sub_map.has_key(language):
                lang_sub_map[language] = []
            lang_sub_map[language].append(basename)

        for language, subs in languages.items():
            part.subtitles[language][basename] = subs

        return lang_sub_map


# noinspection PyBroadException
class DefaultSubtitleHelper(SubtitleHelper):
    @classmethod
    def is_helper_for(cls, filename):
        (file, file_extension) = os.path.splitext(filename)
        return file_extension.lower()[1:] in SUBTITLE_EXTS

    def process_subtitles(self, part):

        lang_sub_map = {}

        basename = os.path.basename(self.filename)
        (file, ext) = os.path.splitext(self.filename)

        # Remove the initial '.' from the extension
        ext = ext[1:]

        forced = ''
        default = ''
        split_tag = file.rsplit('.', 1)
        if len(split_tag) > 1 and split_tag[1].lower() in ['forced', 'normal', 'default']:
            file = split_tag[0]
            # don't do anything with 'normal', we don't need it
            if 'forced' == split_tag[1].lower():
                forced = '1'
            if 'default' == split_tag[1].lower():
                default = '1'

        # Attempt to extract the language from the filename (e.g. Avatar (2009).eng)
        language = ""
        language_match = re.match(r".+\.([^-.]+)(?:-[A-Za-z]{2,4})?$", file)
        if language_match and len(language_match.groups()) == 1:
            language = language_match.groups()[0]

        # Extended Support:
        # - Simplified Chinese Subtitles (chs)
        # - Traditional Chinese Subtitles (cht)
        if language.lower() in ('chs', 'cht'):
            language = Locale.Language.Chinese
        else:
            language = Locale.Language.Match(language)

        codec = None
        format = None
        if ext in ['txt', 'sub']:
            try:
                file_contents = Core.storage.load(self.filename)
                lines = [line.strip() for line in file_contents.splitlines(True)]
                if re.match(r'^\{[0-9]+}\{[0-9]*}', lines[1]):
                    format = 'microdvd'
                elif re.match(r'^[0-9]{1,2}:[0-9]{2}:[0-9]{2}[:=,]', lines[1]):
                    format = 'txt'
                elif '[SUBTITLE]' in lines[1]:
                    format = 'subviewer'
                else:
                    Log("The subtitle file does not have a known format, skipping... : " + self.filename)
                    return lang_sub_map
            except:
                Log("An error occurred while attempting to parse the subtitle file, skipping... : " + self.filename)
                return lang_sub_map

        if codec is None and ext in ['ass', 'ssa', 'smi', 'srt', 'psb']:
            codec = ext.replace('ass', 'ssa')

        if format is None:
            format = codec

        Log('Found subtitle file: ' + self.filename + ' language: ' + language + ' codec: ' + str(
            codec) + ' format: ' + str(format) + ' default: ' + default + ' forced: ' + forced)
        part.subtitles[language][basename] = Proxy.LocalFile(self.filename, codec=codec, format=format, default=default,
                                                             forced=forced)

        lang_sub_map[language] = [basename]
        return lang_sub_map
