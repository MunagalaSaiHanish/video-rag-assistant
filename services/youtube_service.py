from urllib.parse import urlparse, parse_qs


def extract_video_id(url):

    parsed_url = urlparse(url)

    query = parse_qs(parsed_url.query)

    if "v" not in query:
        return None

    return query["v"][0]