import requests
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

class TranscriptSegment:
    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration

def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        try:
            ts = api.list(video_id)
            # Try manually created English transcript
            try:
                transcript = ts.find_manually_created_transcript(['en'])
            except Exception:
                # Try auto-generated English transcript
                try:
                    transcript = ts.find_generated_transcript(['en'])
                except Exception:
                    # Translate any other available language to English
                    all_langs = list(ts._manually_created_transcripts.keys()) + list(ts._generated_transcripts.keys())
                    transcript = ts.find_transcript(all_langs)
                    if transcript.is_translatable:
                        transcript = transcript.translate('en')
            raw_transcript = transcript.fetch()
        except Exception:
            raw_transcript = api.fetch(video_id)

        segments = []
        for entry in raw_transcript:
            segments.append(TranscriptSegment(
                text=entry.get('text', ''),
                start=entry.get('start', 0.0),
                duration=entry.get('duration', 0.0)
            ))
        return segments
    except Exception:
        try:
            ydl_opts = {
                'writeautomaticsub': True,
                'subtitlesformat': 'json3',
                'skip_download': True,
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                subtitles = info.get('requested_subtitles') or info.get('automatic_captions')
                if not subtitles:
                    return None
                lang = 'en' if 'en' in subtitles else list(subtitles.keys())[0]
                sub_info = subtitles[lang]
                url = sub_info.get('url') if isinstance(sub_info, dict) else (sub_info[0].get('url') if isinstance(sub_info, list) and sub_info else None)
                if not url:
                    return None
                if 'fmt=json3' not in url and '&fmt=' not in url:
                    url += '&fmt=json3'
                r = requests.get(url, timeout=10)
                data = r.json()
                events = data.get('events', [])
                segments = []
                for ev in events:
                    start_ms = ev.get('tStartMs', 0)
                    duration_ms = ev.get('dDurationMs', 0)
                    segs = ev.get('segs', [])
                    text = "".join([s.get('utf8', '') for s in segs]).strip()
                    if not text or text == '\n':
                        continue
                    segments.append(TranscriptSegment(text, start_ms / 1000.0, duration_ms / 1000.0))
                return segments
        except Exception:
            return None

def transcript_to_text(transcript):
    full_text = ""
    for segment in transcript:
        full_text += segment.text + " "
    return full_text

def transcript_with_timestamps(transcript):
    segments = []
    for segment in transcript:
        segments.append({
            "text": segment.text,
            "start": segment.start,
            "end": segment.start + segment.duration
        })
    return segments
