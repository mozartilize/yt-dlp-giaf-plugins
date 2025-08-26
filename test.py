from yt_dlp.downloader.fragment import FragmentFD
from yt_dlp.downloader.hls import HlsFD
from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL

# Minimal dummy YDL object
class DummyYDL:
    def __init__(self):
        self.params = {}
    def to_screen(self, msg):
        print(msg)
    def report_error(self, msg):
        print("ERROR:", msg)
    def trouble(self, msg=None):
        raise DownloadError(msg)


if __name__ == "__main__":
    ydl = DummyYDL()

    # Params needed for FragmentFD
    params = {
        'continuedl': True,
        'quiet': False,
        'nopart': False,
        'ratelimit': None,
        'buffersize': 1024,
        'test': False,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'keep_fragments': False,
    }

    mainifest = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-INDEPENDENT-SEGMENTS
#EXT-X-TARGETDURATION:9
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:9.876533,
https://p16-sg.tiktokcdn.com/obj/tos-alisg-avt-0068/a7a587a9f6e265f9a8c0042f5f49f62a
"""

    fd = HlsFD(YoutubeDL({
        'verbose': True,
        'fragment_image_cloaking': True,
        'continue': False,
    }), params)

    info_dict = {
        'hls_media_playlist_data': mainifest,
        'url': 'https://example.com/init.mp4',  # not actually used directly in fragments mode
        'fragment_base_url': None,  # or a string prefix for fragment URLs
        'protocol': 'http',
        'ext': 'mp4',
    }

    success = fd.real_download('output.mp4', info_dict)
