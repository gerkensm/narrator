import io
from typing import Union
from pydub import AudioSegment
from mutagen.mp3 import MP3
import aiohttp
from config import SPEAKER_TO_VOICE_ID, Speaker

async def tts_output(speaker: Speaker, text: str, model_id: str, api_key: str) -> Union[io.BytesIO, None]:
    """
    Generate text-to-speech audio using the ElevenLabs API.

    Args:
        speaker (Speaker): The speaker enum representing the desired voice.
        text (str): The text to be converted to speech.
        model_id (str): The ID of the TTS model to use.
        api_key (str): The ElevenLabs API key.

    Returns:
        io.BytesIO: The generated audio as a BytesIO object, or None if an error occurs.
    """
    voice_id = SPEAKER_TO_VOICE_ID[speaker]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "model_id": model_id,
        "text": text,
        "voice_settings": {
            "similarity_boost": 0.4,
            "stability": 0.4,
            "style": 0.7,
            "use_speaker_boost": True
        }
    }
    headers = {"xi-api-key": api_key}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                audio_buffer_io = io.BytesIO()
                async for chunk in response.content.iter_chunked(1024*1000):
                    audio_buffer_io.write(chunk)
                audio_buffer_io.flush()
                audio_buffer_io.seek(0)
                normalized_audio_buffer = match_target_amplitude(audio_buffer_io, -20)
                return normalized_audio_buffer
            else:
                print(f"Error generating TTS audio: {response.status}")
                return None

def match_target_amplitude(bufferio: io.BytesIO, target_dbfs: int = -10) -> io.BytesIO:
    """
    Normalize the audio amplitude to a target dBFS level.

    Args:
        bufferio (io.BytesIO): The input audio buffer.
        target_dbfs (int): The target dBFS level for normalization.

    Returns:
        io.BytesIO: The normalized audio buffer.
    """
    sound = AudioSegment.from_file(bufferio)
    change_in_dbfs = target_dbfs - sound.dBFS
    normalized_sound = sound.apply_gain(change_in_dbfs)
    outf = io.BytesIO()
    normalized_sound.export(outf, format="mp3")
    outf.seek(0)
    return outf

def get_audio_duration(audio_buffer: io.BytesIO) -> float:
    """
    Get the duration of an audio buffer in seconds.

    Args:
        audio_buffer (io.BytesIO): The input audio buffer.

    Returns:
        float: The duration of the audio in seconds.
    """
    return MP3(audio_buffer).info.length