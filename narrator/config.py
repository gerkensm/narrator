from enum import Enum
from typing import Dict, List
from pydantic_settings import BaseSettings

class Speaker(Enum):
    HERZOG = "Werner Herzog"
    ADORNO = "Theodor W. Adorno"
    ZIZEK = "Slavoj Žižek"

class Settings(BaseSettings):
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    herzog_voice_id: str = '242pUn06d7kxuB5cZdVw'
    adorno_voice_id: str = 'B84LQqhW5ZdidYkT9Cgb'
    zizek_voice_id: str = 'tHSWOxKiMYit2kQAqxTV'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

SPEAKER_TO_VOICE_ID: Dict[Speaker, str] = {
    Speaker.HERZOG: Settings().herzog_voice_id,
    Speaker.ADORNO: Settings().adorno_voice_id,
    Speaker.ZIZEK: Settings().zizek_voice_id,
}

SPEAKER_TO_STYLE_ATTRIBUTES: Dict[Speaker, str] = {
    Speaker.ADORNO: "Complex, critical, dense, interdisciplinary, reflective, abstract, pessimistic, scholarly, multifaceted, provocative",
    Speaker.HERZOG: "Dense, grim, dark, inquisitive, analytical, critical, abstract, complex, philosophical, nuanced, reflective, interdisciplinary, intricate, erudite",
    Speaker.ZIZEK: "Provocative, complex, eclectic, humorous, dense, contradictory, critical, engaging, paradoxical, polemical"
}

SPEAKER_TO_FIRST_NAME: Dict[Speaker, List[str]] = {
    Speaker.HERZOG: ['Werner', "Herzog"],
    Speaker.ADORNO: ["Theo", "Theodor", "Adorno"],
    Speaker.ZIZEK: ['Slavoy', 'Slavoj', "Zizek"],
}