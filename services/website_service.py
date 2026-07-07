import requests

from bs4 import BeautifulSoup


def extract_website_text(url):

    headers = {

        "User-Agent":
        "Mozilla/5.0"

    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException:

        return None

    soup = BeautifulSoup(

        response.text,

        "html.parser"

    )

    for tag in soup(

        [
            "script",
            "style",
            "noscript"
        ]

    ):

        tag.decompose()

    text = soup.get_text(

        separator=" ",

        strip=True

    )

    return text