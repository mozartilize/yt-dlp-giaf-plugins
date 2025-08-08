import re
from typing import override, TYPE_CHECKING
from urllib.parse import urlparse

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import ExtractorError
from yt_dlp.extractor.blogger import BloggerIE
from yt_dlp.utils import js_to_json, traverse_obj, urlencode_postdata

if TYPE_CHECKING:
    from yt_dlp.extractor.common import _InfoDict


# class Viet69IE(InfoExtractor):
class Viet69IE(InfoExtractor):
    _VALID_URL = r"https?:\/\/viet69\.[a-z]+\/[\w\.\-]+\/?"

    @override
    def _real_extract(self, url) -> "_InfoDict":
        video_id = "unknown"
        parsed_url = urlparse(url)
        base_url = parsed_url.scheme + "://" + parsed_url.netloc

        webpage, _ = self._download_webpage_handle(url, video_id)

        m = re.search(r'data-movie="([^"]+)"\s+data-type="([^"]+)"', webpage)
        if not m:
            raise ExtractorError("Can not find data-movie/data-type")

        movie_id, movie_type = m.groups()

        movie_endpoint = base_url + "/get.video.php"
        player_payload = {
            "movie_id": movie_id,
            "type": movie_type,
            "index": 0,
        }
        player_iframe_html, _ = self._download_webpage_handle(
            movie_endpoint,
            movie_id,
            data=urlencode_postdata(player_payload),
            headers={"Referer": base_url},
        )
        iframe_src = self._search_regex(
            r'<iframe[^>]+src="([^"]+)"',
            player_iframe_html,
            "iframe src",
        )

        m = re.search(r"/([0-9a-fA-F-]{36})", iframe_src)
        if m:
            movie_uuid = m.group(1)
        else:
            raise ExtractorError(f"can not find movie_uuid from {iframe_src}")

        player_parsed_url = urlparse(iframe_src)
        player_base_url = player_parsed_url.scheme + "://" + player_parsed_url.netloc
        movie_info, _ = self._download_json_handle(
            player_base_url + "/api/get-video",
            movie_uuid,
            query={"id": movie_uuid},
            headers={"Referer": player_base_url},
        )
        self.write_debug(movie_info["url"])
        blogger_ie = BloggerIE(self._downloader)
        return blogger_ie._real_extract(movie_info["url"])