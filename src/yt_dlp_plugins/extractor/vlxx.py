import re
from typing import TYPE_CHECKING, override
from urllib.parse import urlparse

import yt_dlp.downloader.fragment
from yt_dlp.downloader.fragment import FragmentFD
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import js_to_json, traverse_obj, urlencode_postdata

if TYPE_CHECKING:
    from yt_dlp.extractor.common import _InfoDict


class VlxxIE(InfoExtractor):
    _VALID_URL = r"https?:\/\/vlxx\.[a-z]+\/video\/[\w\.\-]+\/(?P<id>\d+)\/?"

    @override
    def _real_extract(self, url) -> "_InfoDict":
        video_id = self._match_id(url)
        parsed_url = urlparse(url)
        base_url = parsed_url.scheme + "://" + parsed_url.netloc

        ajax_endpoint = base_url + "/ajax.php"
        player_info_request_payload = {
            "vlxx_server": 1,
            "id": video_id,
            "server": 1,
        }

        player_info = self._download_json(
            ajax_endpoint,
            video_id,
            data=urlencode_postdata(player_info_request_payload),
        )

        player_iframe_html = player_info["player"]
        iframe_src = self._search_regex(
            r'<iframe[^>]+src="([^"]+)"',
            player_iframe_html,
            "iframe src",
        )

        iframe_src_parsed = urlparse(iframe_src)
        referer = iframe_src_parsed.scheme + "://" + iframe_src_parsed.netloc

        # 3. Download the iframe HTML page
        iframe_webpage = self._download_webpage(iframe_src, video_id)

        # Step 3: Extract and parse just the `sources: [...]` array
        sources_json_str = self._search_regex(
            r"sources\s*:\s*(\[\s*{.*?}\s*\])",
            iframe_webpage,
            "sources array",
            flags=re.DOTALL,
        )
        sources = self._parse_json(js_to_json(sources_json_str), video_id)

        # Step 4: Pick first playable source
        video_url = traverse_obj(sources, (0, "file"))

        formats = self._extract_m3u8_formats(video_url, video_id, ext="mp4")

        return {
            "age_limit": 16,
            "id": video_id,
            "availability": "public",
            "formats": formats,
            "http_headers": {
                "Origin": referer,
                "Referer": referer,
            },
        }


class PngStripFD(FragmentFD):
    def _append_fragment(self, ctx, frag_content):
        frag_content = frag_content[9:]
        super()._append_fragment(ctx, frag_content)


yt_dlp.downloader.fragment.FragmentFD = PngStripFD
