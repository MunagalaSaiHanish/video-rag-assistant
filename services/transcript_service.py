import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
)


# ---------------------------------------------------------------------------
# Fetch transcript  (raises on transient failures so the caller can show
# the real error instead of the misleading "no transcript available").
# ---------------------------------------------------------------------------

MAX_RETRIES = 2
RETRY_DELAY = 2          # seconds between retries


def get_transcript(video_id):
    """
    Returns a FetchedTranscript on success.
    Returns None ONLY when the video genuinely has no transcript.
    Raises on transient errors (IP block, network, etc.) so the caller
    can display the real message.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)
            return transcript

        except (NoTranscriptFound, TranscriptsDisabled):
            # Video truly has no transcript — don't retry
            return None

        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    # All retries exhausted — raise so the UI can show the real error
    raise RuntimeError(
        f"Could not fetch transcript after {MAX_RETRIES} attempts: {last_error}"
    )


# ---------------------------------------------------------------------------
# Convert transcript into plain text
# ---------------------------------------------------------------------------

def transcript_to_text(transcript):

    full_text = ""

    for segment in transcript:

        full_text += segment.text + " "

    return full_text


# ---------------------------------------------------------------------------
# Extract transcript with timestamps
# ---------------------------------------------------------------------------

def transcript_with_timestamps(transcript):

    segments = []

    for segment in transcript:

        segments.append(
            {
                "text": segment.text,
                "start": segment.start,
                "end": segment.start + segment.duration
            }
        )

    return segments