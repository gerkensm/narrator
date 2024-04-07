# Narrator

Welcome to Narrator, a Python package that brings together the power of OpenAI's GPT-4 and ElevenLabs' text-to-speech APIs to create a unique, interactive narration experience. With Narrator, you can sit back and watch as renowned intellectuals Werner Herzog, Theodor W. Adorno, and Slavoj Žižek provide live commentary on your programming endeavors. Because who wouldn't want a trio of philosophical heavyweights critiquing their code?

The tool has been developed for Mac OS - some parts, especially the subtitle overlays, are highly specific to Mac OS' APIs.

## Features

- Real-time narration by your choice of Werner Herzog, Theodor W. Adorno, and/or Slavoj Žižek
- Live commentary based on your webcam feed and screen captures
- Customizable text-to-speech voices powered by ElevenLabs
- Optional subtitle overlays to keep track of the intellectual discourse
- Seamless integration with OpenAI's GPT-4 Vision for generating insightful (and occasionally baffling) commentary
- A command-line interface that's as easy to use as it is to pronounce "Žižek"

## Installation

Before you embark on this auditory adventure, make sure you have Python 3.6 or later installed.

Then, simply run:

```
pip install narrator
```

And voila! You're ready to have your coding sessions narrated by some of the most influential thinkers of our time.

## Usage

To start a narration session, open your terminal and run:

```
narrator [OPTIONS]
```

The available options include:

- `--disable-subtitles`: Disable subtitle overlays (for a more immersive, albeit potentially confusing, experience)
- `--disable-adorno`: Exclude Theodor W. Adorno from the narration (in case you find his critical theory a bit too critical)
- `--disable-herzog`: Exclude Werner Herzog from the narration (if you prefer your commentary without existential dread)
- `--disable-zizek`: Exclude Slavoj Žižek from the narration (because sometimes you just can't handle the Žižek)
- `--tts-model-id`: Choose the ElevenLabs TTS model ID (for when you need a change of voice)
- `--disable-override-next-speaker`: Disable overriding the next speaker based on mentions in the previous narration (for a more chaotic conversation)
- `--subtitles-text-color`: Set the subtitle text color (to match your IDE's color scheme, of course)
- `--subtitles-font-size`: Set the subtitle font size (for those times when the commentary is just too profound)
- `--subtitles-font`: Set the subtitle font (because even intellectuals appreciate good typography)
- `--subtitles-shadow-color`: Set the subtitle shadow color (for that extra touch of depth)
- `--subtitles-shadow-offset-x`: Set the subtitle shadow offset on the X-axis (when you need to fine-tune your shadow game)
- `--subtitles-shadow-offset-y`: Set the subtitle shadow offset on the Y-axis (same as above, but vertically)
- `--subtitles-shadow-blur-radius`: Set the subtitle shadow blur radius (for a softer, more contemplative look)
- `--subtitles-shadow-alpha`: Set the subtitle shadow opacity (when you need to dial back the drama)
- `--subtitles-font-alpha`: Set the subtitle font opacity (for those moments when the commentary starts to fade)
- `--herzog-voice-id`: Set the voice ID for Werner Herzog (in case you find a voice that captures his essence better)
- `--adorno-voice-id`: Set the voice ID for Theodor W. Adorno (same as above, but for Adorno)
- `--zizek-voice-id`: Set the voice ID for Slavoj Žižek (you get the idea)
- `--openai-api-key`: Set the OpenAI API key (because even brilliant minds need access keys)
- `--elevenlabs-api-key`: Set the ElevenLabs API key (same as above, but for ElevenLabs)

For more information on any of these options, just run `narrator --help`. We've got you covered.

## Configuration

In addition to the command-line options, you can also set your OpenAI and ElevenLabs API keys, as well as the default voice IDs for each narrator, in a `.env` file. Just create a file named `.env` in your project directory and add the following lines:

```
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
HERZOG_VOICE_ID=your_herzog_voice_id_here
ADORNO_VOICE_ID=your_adorno_voice_id_here
ZIZEK_VOICE_ID=your_zizek_voice_id_here
```

Replace the placeholders with your actual API keys and voice IDs, and Narrator will automatically use these values when you run the program.

## Contributing

We welcome contributions from fellow enthusiasts of philosophy, programming, and quirky side projects. If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

We'll review your changes and merge them if they align with the project's goals and meet our coding standards. And who knows, maybe your contributions will catch the attention of our esteemed narrators!

## License

This project is licensed under the [Add your chosen license here]. See the `LICENSE` file for more information.

## Acknowledgments

We'd like to thank the following individuals and organizations for their invaluable contributions to this project:

- OpenAI for providing the GPT-4 language model that powers the narration
- ElevenLabs for their impressive text-to-speech API
- Werner Herzog, Theodor W. Adorno, and Slavoj Žižek for their groundbreaking work in philosophy, film, and cultural criticism (and for unwittingly lending their voices to this project)
- The open-source community for creating the libraries and tools that made this project possible

And of course, a special thanks to you, the user, for embarking on this strange and wonderful journey with us. Happy narrating!
