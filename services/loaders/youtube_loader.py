from services.youtube_service import extract_video_id
from services.transcript_service import (
    get_transcript,
    transcript_to_text
)

from services.youtube_metadata import get_video_metadata

from services.models.document import Document


def load_youtube(url):

    video_id = extract_video_id(url)

    if video_id is None:

        return None

    transcript = get_transcript(video_id)

    if transcript is None:

        return None

    text = transcript_to_text(
        transcript
    )

    metadata = get_video_metadata(
        url
    )

    document = Document.create(

        source="youtube",

        title=metadata["title"],

        content=text,

        metadata={

            "channel": metadata["channel"],

            "thumbnail": metadata["thumbnail"],

            "url": url

        }

    )

    return document