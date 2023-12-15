from base64 import urlsafe_b64decode
from posixpath import basename
from urlparse import urlparse


def NormalizeURL(url):
    return url


def MetadataObjectForURL(url):
    return VideoClipObject(
        title='Trailer',
    )


def MediaObjectsForURL(url):
    url = urlparse(url)
    url = basename(url.path)
    url = urlsafe_b64decode(url)

    if not Regex(r'^https?:\/\/.+').match(url):
        return []

    return [
        MediaObject(
            parts=[
                PartObject(key=Callback(
                    PlayVideo, url=url
                ))
            ],
            optimized_for_streaming=True
        )
    ]


@indirect
def PlayVideo(url, *args, **kwargs):
    Log.Debug('Playing trailer: "%s"' % url)
    return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url))
