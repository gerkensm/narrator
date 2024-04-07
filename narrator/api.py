import re
import io
from openai import AsyncOpenAI
from typing import List
from config import SPEAKER_TO_STYLE_ATTRIBUTES, SPEAKER_TO_FIRST_NAME, Speaker
from image import image_to_base64
from typing import Tuple

def other_speakers(speaker: Speaker, selected_speakers: List[Speaker]) -> str:
    """
    Get the names of the other selected speakers.

    Args:
        speaker (Speaker): The current speaker.
        selected_speakers (List[Speaker]): The list of selected speakers.

    Returns:
        str: The names of the other selected speakers.
    """
    return " and ".join([s.value for s in selected_speakers if s != speaker])

def get_next_speaker(speaker: Speaker, last_message: str, selected_speakers: List[Speaker], override_next_speaker: bool) -> Speaker:
    """
    Determine the next speaker based on the last message and selected speakers.

    Args:
        speaker (Speaker): The current speaker.
        last_message (str): The last message in the conversation.
        selected_speakers (List[Speaker]): The list of selected speakers.
        override_next_speaker (bool): Whether to override the next speaker if mentioned in the last message.

    Returns:
        Speaker: The next speaker.
    """
    if override_next_speaker and last_message:
        for other_speaker, first_name_list in SPEAKER_TO_FIRST_NAME.items():
            if other_speaker in selected_speakers and other_speaker != speaker:
                for first_name in first_name_list:
                    if first_name.lower() in last_message.lower():
                        print(f"{other_speaker.value} mentioned directly in message. Giving them the next turn.")
                        return other_speaker

    next_idx = (selected_speakers.index(speaker) + 1) % len(selected_speakers)
    return selected_speakers[next_idx]

async def react(speaker: Speaker, webcam_image_bytes_io: io.BytesIO, screenshot_bytes_io: io.BytesIO,
                history: List[str], selected_speakers: List[Speaker], client: AsyncOpenAI) -> Tuple[str, str]:
    """
    Generate a reaction from the specified speaker based on the provided images and conversation history.

    Args:
        speaker (Speaker): The current speaker.
        webcam_image_bytes_io (io.BytesIO): The webcam image as a BytesIO object.
        screenshot_bytes_io (io.BytesIO): The screenshot image as a BytesIO object.
        history (List[str]): The conversation history.
        selected_speakers (List[Speaker]): The list of selected speakers.
        client (AsyncOpenAI): The OpenAI API client.

    Returns:
        Tuple[str, str]: A tuple containing the speaker name and the generated reaction.
    """
    webcam_image_base64_url = image_to_base64(webcam_image_bytes_io)
    screenshot_base64_url = image_to_base64(screenshot_bytes_io)
    speaker_name = speaker.value
    style = SPEAKER_TO_STYLE_ATTRIBUTES[speaker]
    other_speaker_names = other_speakers(speaker, selected_speakers)
    history_messages = [{"role": "assistant", "content": [{"type": "text", "text": msg}]} for msg in history]

    prompt_and_messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"""Pretend you are {speaker_name}. 
You co-narrate a computer scientist doing work in the style of one of your works, 
together with your colleagues {other_speaker_names} (which you address informally, 
e.g., by "you" or their first name) in a highly conversational style. 

Your tone and linguistic style is {style}. 
You drive a conversation with your co-narrators about the observed scene. 

You often compare observations or analyses from the scene to examples from 
your works or the works and topics of your colleagues. You are supplied with 
an image from the webcam of the software engineer and a screenshot to drive your narration.

{"React directly to the last comment of your co-narrator from the message history, if any, and continue their or your own line of thinking. You may address your co-narrators and express your agreement or disagreement with their statements, or add your own view on the analysis or observation." if history else ""}

Specifically comment on what the programmer looks like in the webcam image and what the 
developer is currently doing, holding, or doing with their hands. 

Is he smoking an e-cigarette? Is he drinking? What is he wearing? 
What is his hair style? Is he shaved? 
Comment on these actions and details if they are present. 
Also look for details and actions in both images, and narrate them. 
Only comment on these if the developer is actually doing them - not on their absence. 
E.g., if the user is not smoking, don't comment on him not smoking.

You may also infer what the user is programming based on the code visible in the screenshot 
and use that for your narration.

Never mention the source - the two images you're presented with directly. 
Describe the images, narrate what's happening, but don't mention "the first image" or "the second image" - 
just comment on the content of the scenes you're perceiving.

Generate EXACTLY 2 sentences in the style of {speaker_name}, without any pre-text, 
just the reaction to previous messages and/or narration. Do not generate more text.

{"In these two sentences, react directly to the last comment of your co-narrator from the message history, and continue their or your own line of thinking." if history else ""}

You may address your co-narrator (informally, e.g., by their first name) and express your agreement 
or disagreement with their last statements, or add your own view on the last analysis or observation. 

You may occasionally address them directly and share your thoughts on their narration, before adding your 
own observations. Create a true dialogue between the two narrators. Answer questions from your co-narrator. 

Often ask your co-narrator questions on their views regarding the observed! 
You often compare observations or analyses from the scene to examples from your works - 
or you may address your co-narrators' works and draw comparisons from that. Be bold and provocative, 
also towards your co-narrators. Challenge them. Call them out. 
Disagree with their theories if it goes against the theoretical belief of your character.

Do not repeat previous observations without adding new aspects. 
Focus on different observations or aspects every time.
Do NOT prefix your message with your speaker name."""
                },
            ],
        },
        *history_messages
    ]

    messages = [
        *prompt_and_messages,
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Here is a current image of the programmer, shot via the webcam:"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": webcam_image_base64_url,
                        "detail": "high"
                    }
                },
                {
                    "type": "text",
                    "text": "Here is a current image of the screen that the programmer sees:"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": screenshot_base64_url,
                        "detail": "high"
                    }
                },
            ],
        }
    ]

    while True:
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=300,
            temperature=1.0,
        )
        reaction = response.choices[0].message.content
        reaction = re.sub(r"\[.*\]", "", reaction).strip()
        if "I'm sorry, I cannot provide that information." not in reaction:
            break

    return speaker_name, reaction