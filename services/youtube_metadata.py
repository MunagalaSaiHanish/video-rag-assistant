import requests


def get_video_metadata(video_url):

    endpoint = "https://www.youtube.com/oembed"

    params = {
        "url": video_url,
        "format": "json"
    }

    try:

        response = requests.get(
            endpoint,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return {
            "title": data.get("title", ""),
            "channel": data.get("author_name", ""),
            "thumbnail": data.get("thumbnail_url", "")
        }

    except Exception:

        return None