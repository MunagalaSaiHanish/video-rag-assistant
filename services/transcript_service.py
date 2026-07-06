from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import IpBlocked


#fetch transcript

def get_transcript(video_id):

    try:

        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        return transcript

    except IpBlocked:

        return None


#convert transcript into plain text

def transcript_to_text(transcript):

    full_text = ""

    for segment in transcript:

        full_text += segment.text + " "

    return full_text


#extract transcript with timestamps

#extract transcript with timestamps

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