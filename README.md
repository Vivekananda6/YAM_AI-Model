# YAM AI Assistant

YAM is a Python desktop assistant for voice and text commands, everyday tasks, and optional cloud AI. Without an API key, it uses a small rules-based fallback for common requests.

## Overview

The application runs locally. Cloud chat replies require a compatible API key; without one, YAM handles a limited set of common requests. Optional integrations are skipped when their packages or services are unavailable.

The application includes:

- AI assistant behavior and response logic
- voice output through `pyttsx3` or `gTTS`
- speech recognition support through `SpeechRecognition`
- note and task management with saved memory
- daily brief and smart planning features
- web search and app launching
- prompt-card image creation using Pillow; this is not text-to-image model generation
- OpenAI-compatible API support via environment variables
- graphical desktop interface using Tkinter
- safe confirmation checks for destructive or system-level actions

## Project structure

- `AI_YAM/AI_YAM.py` – main application logic and GUI
- `requirements.txt` – project dependencies
- `.env.example` – sample environment configuration for real AI backend use
- `start_yam.bat` – the single Windows start option; launches the packaged app when present, otherwise runs the Python source
- `AI_YAM/resources/` – generated resources such as memory files and generated media
- `USAGE_GUIDE.md` and `WORKFLOW.md` – setup, usage, and interaction details
- `YAM_AI_Assistant.spec` – PyInstaller build configuration
- `dist/` – packaged executable output when built with PyInstaller

## Features

### Core assistant capabilities

- greeting and conversational responses
- time and date queries
- daily brief generation
- smart planning for tasks and goals
- notes memory and saved reminders
- task creation and completion tracking
- search and web browsing shortcuts
- Windows Camera and Settings shortcuts
- app launching for common tools like calculator, notepad, and browser
- weather lookup support
- Wikipedia search with a short page summary
- joke responses

### AI and productivity features

- rules-based local replies when no external API key is supplied
- OpenAI-compatible chat completions through the YAM API settings
- AI chat prompts through natural language commands
- recent-note review locally, with summarization through cloud AI when configured
- a styled image card containing a prompt, created with Pillow
- text-to-audio conversion for spoken responses
- audio-to-text transcription when a valid audio file is provided

### Desktop experience

- modern dark-themed Tkinter interface
- chat tab and dashboard tab
- status updates and quick action buttons
- live system overview for notes, tasks, and AI configuration

## Voice input

Click **Push to Talk** once, speak one command, and pause briefly. YAM captures a phrase, runs it, speaks the reply, and returns to ready; no wake word is needed. The recognized command and reply appear in chat. If microphone or speech input fails, the UI focuses the typed-command box. If speech output fails, the reply stays visible and the UI reports the error.

## Installation

1. Open a terminal in the project root.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. If you want cloud AI support, create your environment file:

```bash
copy .env.example .env
```

4. Edit the `.env` file and add your relevant values.

5. Start the assistant using the single launcher in the project root:

```text
start_yam.bat
```

To build a Windows executable, install PyInstaller and build from the project root:

```bash
pip install pyinstaller
pyinstaller --clean YAM_AI_Assistant.spec
```

## Environment variables

The application checks several environment variable names for cloud AI integration. A sample configuration is included in `.env.example`.

Example:

```env
YAM_API_KEY=your_api_key_here
YAM_API_BASE_URL=https://api.openai.com/v1
YAM_AI_MODEL=gpt-4o-mini
YAM_AI_PROVIDER=openai
```

The assistant also supports fallback environment names such as:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`

If no key is configured, the project still runs in local fallback mode. That fallback uses simple rules; it does not provide general neural-network reasoning.

## Usage examples

Try commands such as:

- hello
- how are you
- what time is it
- what is the date
- search for python tutorials
- open google
- open calculator
- add task prepare presentation
- show tasks
- daily brief
- summarize notes
- smart plan for my day
- ask ai plan my day
- open camera
- open settings
- open camera settings
- search wikipedia for Saturn
- generate image futuristic city skyline at night
- convert text to audio hello world
- transcribe audio file path
- remember project meeting at 5 pm
- show my notes

## Safety and system actions

Some commands can affect the operating system. These are protected by confirmation logic to reduce accidental risk.

Examples:

- shutdown
- restart
- lock window
- empty recycle bin

The assistant asks for explicit confirmation before performing these actions.

## System requirements

- Python 3.10 or newer recommended
- Windows is the primary target, but much of the logic is cross-platform friendly
- Microphone support is optional; keyboard input is used as a fallback
- Internet access is needed for web search and cloud AI features

## Troubleshooting

### Import errors

If Python cannot import a package, reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Mic or voice issues

- Ensure microphone permissions are allowed
- Confirm the system has a working microphone
- Speech recognition uses an online service and needs internet access
- If capture or recognition fails, use the focused text input in the app

### AI backend not responding

- Check the `.env` file values
- Verify the API key is valid
- Confirm your base URL is correct
- If no API key is set, the built-in local fallback continues to work

### GUI not opening

Start YAM using `start_yam.bat`. If you are running from source and need error details, launch that batch file from PowerShell in the project directory.

## Notes

- The app automatically creates missing resource files and default memory files when needed.
- Local replies use simple rules; richer chat replies require an API key and internet access.
- The image command creates a prompt card, not a scene synthesized by an AI image model.
- Saved notes and tasks stay local. Source runs use `AI_YAM/resources/memory.json`; a packaged executable stores them in a `resources` folder beside the executable.

## License

No license file is included, so redistribution and reuse terms have not been specified.
