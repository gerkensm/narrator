import time
import random
import asyncio
import click
import os
from typing import List

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pygame import mixer
from openai import AsyncOpenAI

from .config import SPEAKER_TO_VOICE_ID, Settings, Speaker
from .audio import tts_output, get_audio_duration
from .image import capture_screen, capture_cam
from .api import react, get_next_speaker
from .overlay import SubtitleOverlay

settings = Settings()

async def async_main(client: AsyncOpenAI, disable_subtitles: bool, selected_speakers: List[Speaker], tts_model_id: str,
                     disable_override_next_speaker: bool, subtitles_text_color: str = None, subtitles_font_size: int = None,
                     subtitles_font: str = None, subtitles_shadow_color: str = None, subtitles_shadow_offset_x: float = None,
                     subtitles_shadow_offset_y: float = None, subtitles_shadow_blur_radius: int = None, subtitles_shadow_alpha: float = None,
                     subtitles_font_alpha: float = None):
    """
    The main asynchronous function that orchestrates the narration process.

    Args:
        disable_subtitles (bool): Whether to disable subtitle display.
        selected_speakers (List[Speaker]): The list of selected speakers.
        tts_model_id (str): The ID of the TTS model to use.
        disable_override_next_speaker (bool): Whether to disable overriding the next speaker based on mentions.
        subtitles_text_color (str): The color of the subtitle text. Defaults to the overlay's default value.
        subtitles_font_size (int): The font size of the subtitle text. Defaults to the overlay's default value.
        subtitles_font (str): The font of the subtitle text. Defaults to the overlay's default value.
        subtitles_shadow_color (str): The color of the subtitle shadow. Defaults to the overlay's default value.
        subtitles_shadow_offset_x (float): The X offset of the subtitle shadow. Defaults to the overlay's default value.
        subtitles_shadow_offset_y (float): The Y offset of the subtitle shadow. Defaults to the overlay's default value.
        subtitles_shadow_blur_radius (int): The blur radius of the subtitle shadow. Defaults to the overlay's default value.
        subtitles_shadow_alpha (float): The alpha value of the subtitle shadow. Defaults to the overlay's default value.
        subtitles_font_alpha (float): The alpha value of the subtitle font. Defaults to the overlay's default value.
    """
    subtitle_kwargs = {}
    if subtitles_text_color is not None:
        subtitle_kwargs['text_color'] = subtitles_text_color
    if subtitles_font_size is not None:
        subtitle_kwargs['font_size'] = subtitles_font_size
    if subtitles_font is not None:
        subtitle_kwargs['font'] = subtitles_font
    if subtitles_shadow_color is not None:
        subtitle_kwargs['shadow_color'] = subtitles_shadow_color
    if subtitles_shadow_offset_x is not None and subtitles_shadow_offset_y is not None:
        subtitle_kwargs['shadow_offset'] = (subtitles_shadow_offset_x, subtitles_shadow_offset_y)
    if subtitles_shadow_blur_radius is not None:
        subtitle_kwargs['shadow_blur_radius'] = subtitles_shadow_blur_radius
    if subtitles_shadow_alpha is not None:
        subtitle_kwargs['shadow_alpha'] = subtitles_shadow_alpha
    if subtitles_font_alpha is not None:
        subtitle_kwargs['font_alpha'] = subtitles_font_alpha
    if not disable_subtitles:
        subtitle_overlay = SubtitleOverlay()
    history = []
    play_time = time.time()
    speaker = random.choice(selected_speakers)
    screen = await capture_screen()
    cam = await capture_cam()
    react_promise = asyncio.create_task(react(speaker, cam, screen, history, selected_speakers, client))
    current_subtitle = None

    while True:
        speaker_name, reaction = await react_promise
        next_subtitle = f"{speaker.value}: {reaction}"
        print(next_subtitle)
        history.append(f"[{speaker_name}:] {reaction}")
        output_promise = asyncio.create_task(tts_output(speaker, reaction, tts_model_id, settings.elevenlabs_api_key))
        speaker = get_next_speaker(speaker, reaction, selected_speakers, not disable_override_next_speaker)


        if not disable_subtitles:
            subtitle_overlay.clearSubtitle()
        screen = await capture_screen()
        if not disable_subtitles and current_subtitle:
            subtitle_overlay.setSubtitle(current_subtitle, **subtitle_kwargs)
        
        cam = await capture_cam()
        react_promise = asyncio.create_task(react(speaker, cam, screen, history, selected_speakers, client))

        if play_time > time.time():
            await asyncio.sleep(play_time - time.time())

        output_audio_buffer = await output_promise
        mixer.music.load(output_audio_buffer)
        if not disable_subtitles and next_subtitle:
            current_subtitle = next_subtitle
            subtitle_overlay.setSubtitle(current_subtitle, **subtitle_kwargs)

        mixer.music.play()
        play_time = time.time() + get_audio_duration(output_audio_buffer)

@click.command()
@click.option("--disable-subtitles", is_flag=True, help="Disable subtitle overlays.")
@click.option("--disable-adorno", is_flag=True, help="Exclude Theodor W. Adorno from the narration.")
@click.option("--disable-herzog", is_flag=True, help="Exclude Werner Herzog from the narration.")
@click.option("--disable-zizek", is_flag=True, help="Exclude Slavoj Žižek from the narration.")
@click.option("--tts-model-id", type=click.Choice(["eleven_monolingual_v1", "eleven_multilingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2"]), default="eleven_multilingual_v2", help="Choose the TTS model ID.")
@click.option("--disable-override-next-speaker", is_flag=True, help="Disable overriding the next speaker if another speaker is mentioned in the previous narration.")
@click.option("--subtitles-text-color", default=None, help="Set the subtitle text color.")
@click.option("--subtitles-font-size", type=int, default=None, help="Set the subtitle font size.")
@click.option("--subtitles-font", default=None, help="Set the subtitle font.")
@click.option("--subtitles-shadow-color", default=None, help="Set the subtitle shadow color.")
@click.option("--subtitles-shadow-offset-x", type=float, default=None, help="Set the subtitle shadow offset X.")
@click.option("--subtitles-shadow-offset-y", type=float, default=None, help="Set the subtitle shadow offset Y.")
@click.option("--subtitles-shadow-blur-radius", type=int, default=None, help="Set the subtitle shadow blur radius.")
@click.option("--subtitles-shadow-alpha", type=float, default=None, help="Set the subtitle shadow alpha.")
@click.option("--subtitles-font-alpha", type=float, default=None, help="Set the subtitle font alpha.")
@click.option("--herzog-voice-id", default=None, help="Set the voice ID for Werner Herzog.")
@click.option("--adorno-voice-id", default=None, help="Set the voice ID for Theodor W. Adorno.")
@click.option("--zizek-voice-id", default=None, help="Set the voice ID for Slavoj Žižek.")
@click.option("--openai-api-key", default=None, help="Set the OpenAI API key.")
@click.option("--elevenlabs-api-key", default=None, help="Set the ElevenLabs API key.")
def main(disable_subtitles: bool, disable_adorno: bool, disable_herzog: bool, disable_zizek: bool, tts_model_id: str,
         disable_override_next_speaker: bool, subtitles_text_color: str, subtitles_font_size: int, subtitles_font: str,
         subtitles_shadow_color: str, subtitles_shadow_offset_x: float, subtitles_shadow_offset_y: float,
         subtitles_shadow_blur_radius: int, subtitles_shadow_alpha: float, subtitles_font_alpha: float,
         herzog_voice_id: str, adorno_voice_id: str, zizek_voice_id: str, openai_api_key: str, elevenlabs_api_key: str):
    """
    The main function that sets up the narration process based on the provided CLI options.
    """
    if openai_api_key:
        settings.openai_api_key = openai_api_key
    if elevenlabs_api_key:
        settings.elevenlabs_api_key = elevenlabs_api_key

    if not settings.openai_api_key:
        raise click.UsageError("OpenAI API key is missing. Please provide it using --openai-api-key, provide it as an environment variable, or set it in the .env file.")
    if not settings.elevenlabs_api_key:
        raise click.UsageError("ElevenLabs API key is missing. Please provide it using --elevenlabs-api-key, provide it as an environment variable, or set it in the .env file.")

    selected_speakers = [Speaker.ADORNO, Speaker.HERZOG, Speaker.ZIZEK]
    if disable_adorno:
        selected_speakers.remove(Speaker.ADORNO)
    if disable_herzog:
        selected_speakers.remove(Speaker.HERZOG)
    if disable_zizek:
        selected_speakers.remove(Speaker.ZIZEK)

    if not selected_speakers:
        raise click.UsageError("At least one speaker must be selected.")

    if herzog_voice_id:
        SPEAKER_TO_VOICE_ID[Speaker.HERZOG] = herzog_voice_id
    if adorno_voice_id:
        SPEAKER_TO_VOICE_ID[Speaker.ADORNO] = adorno_voice_id
    if zizek_voice_id:
        SPEAKER_TO_VOICE_ID[Speaker.ZIZEK] = zizek_voice_id

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    asyncio.run(async_main(client, disable_subtitles, selected_speakers, tts_model_id, disable_override_next_speaker,
                           subtitles_text_color, subtitles_font_size, subtitles_font, subtitles_shadow_color,
                           subtitles_shadow_offset_x, subtitles_shadow_offset_y, subtitles_shadow_blur_radius,
                           subtitles_shadow_alpha, subtitles_font_alpha))

if __name__ == "__main__":
    mixer.init()
    main()