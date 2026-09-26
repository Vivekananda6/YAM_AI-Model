# YAM AI Assistant Usage Guide

This guide explains how to install and use the YAM desktop assistant.

## 1. Project purpose

YAM is a Python-based AI assistant that can:

- respond to text and voice commands
- manage tasks and notes
- open websites and apps
- answer daily questions
- create a Pillow image card containing a prompt; this does not synthesize an image
- convert text to audio
- transcribe audio to text
- use a local fallback AI engine when no external API is configured

## 2. Project files

- `AI_YAM/AI_YAM.py` — main assistant code
- `start_yam.bat` — the single Windows start option
- `requirements.txt` — project dependencies
- `.env.example` — sample environment configuration
- `README.md` — project overview

## 3. Requirements

Before running YAM, make sure you have:

- Python 3.10 or newer
- Windows recommended for full feature support
- internet access for web search and cloud AI usage
- microphone access if using voice input

## 4. Install dependencies

Open a terminal in the project root and run:

```bash
pip install -r requirements.txt
```

If you want cloud AI support, also create a `.env` file from the sample:

```bash
copy .env.example .env
```

Then edit `.env` and add your API settings, for example:

```env
YAM_API_KEY=your_api_key_here
YAM_API_BASE_URL=https://api.openai.com/v1
YAM_AI_MODEL=gpt-4o-mini
YAM_AI_PROVIDER=openai
```

If no valid API key is provided, YAM still works in local fallback mode.

## 5. Start the project

### Start YAM

```text
start_yam.bat
```

## 6. Typical usage flow

Once the app starts, you can do the following:

### Voice input in the desktop app

1. Click **Push to Talk** once. The UI changes to `MIC ON | SPEAK NOW`.
2. Speak one command, such as `what time is it` or `add task prepare presentation`, then pause briefly.
3. YAM transcribes and runs that phrase; no wake word is required.
4. The recognized command and YAM's spoken reply appear in chat.
5. The UI returns to `MIC READY | PRESS TO TALK` after the command.

Command transcription tries online recognition and falls back to the installed offline recognizer. If microphone capture fails, YAM focuses the typed-command box. If speech output fails, the text reply stays visible and the UI reports the speaker error.

### A. Basic conversation

Try commands like:

- hello
- hi
- how are you
- what time is it
- what is the date
- who is Albert Einstein
- tell me a joke

### B. Productivity commands

Examples:

- add task prepare presentation
- show tasks
- complete task 1
- remember project meeting at 5 pm
- show my notes
- daily brief
- smart plan for my day

### C. Search and open apps

Examples:

- open google
- open youtube
- open calculator
- open notepad
- open camera
- open settings
- open camera settings
- open sound settings
- search for python tutorials

### D. Wikipedia lookup

Examples:

- `search wikipedia for Saturn`
- `look up Ada Lovelace on Wikipedia`

YAM searches Wikipedia and speaks a short summary of the first matching page. Internet access is required.

### E. AI chat commands

Examples:

- ask ai plan my day
- ask ai summarize my work
- ask ai help me write a message
- chat with ai create a to-do list

### F. Media and generation

Examples:

- generate image futuristic city skyline at night
- convert text to audio hello world
- audio to text sample.wav

### G. Dangerous or system actions

These require confirmation:

- shutdown
- restart
- lock window
- empty recycle bin

Example:

```text
confirm shutdown
```

## 7. Detailed workflow

### Workflow 1: Start and use the app

1. Open the terminal in the project folder.
2. Install requirements.
3. Start the app by opening `start_yam.bat`.
4. The banner appears with the YAM identity.
5. The app loads its memory and command data.
6. The interface opens in the desktop window.
7. You can type or speak commands.

### Workflow 2: Create and manage tasks

1. Type: `add task prepare presentation`
2. YAM saves it in memory.
3. Type: `show tasks` to view saved tasks.
4. Type: `complete task 1` to mark the first task done. Task numbers start at 1.
5. The task file updates automatically.

### Workflow 3: Save notes and generate summaries

1. Type: `remember project meeting at 5 pm`
2. Type: `show my notes`
3. Type: `summarize notes`
4. With cloud AI configured, YAM summarizes the notes. Without it, YAM lists the five most recent notes.

### Workflow 4: Use AI features

1. Type: `ask ai plan my day`
2. YAM processes the request using the local fallback or external API if configured.
3. The result is spoken or shown in the app.

### Workflow 5: Create a prompt card

1. Type: `generate image futuristic robot city at night`.
2. YAM creates a styled prompt card in the resources folder; it does not synthesize a new scene.
3. The output path is shown in the app.

### Workflow 6: Use speech features

1. Type: `convert text to audio hello world`
2. YAM creates an audio file.
3. Type: `audio to text path/to/file.wav` to transcribe it.

## 8. Default behavior when AI is not configured

If no API key is available:

- YAM still runs
- it uses a built-in fallback logic engine
- it keeps basic assistant functionality working
- it can still manage notes, tasks, web opening, and daily planning

## 9. Troubleshooting

### App does not start

Check:

- Python is installed
- dependencies are installed
- file paths are correct
- you are in the correct folder

### No voice output

Check:

- audio engine is available
- system sound outputs are functioning
- microphone permission is enabled

### No speech recognition

Check:

- microphone is connected
- microphone access is enabled
- speech recognition library is installed
- internet access is available for online recognition
- if voice mode reports an error, enter the command in the focused text box

### AI not using your API

Check:

- `.env` exists
- environment variables are valid
- the base URL is correct
- the key is active

## 10. Best practice

For a smooth experience:

- keep Python and dependencies updated
- store API keys in `.env` instead of hardcoding them
- use keyboard fallback when microphone input fails
- confirm system commands before running them
- back up saved notes and tasks if you want long-term records

## 11. Quick start example

```bash
pip install -r requirements.txt
```

Then open `start_yam.bat` from File Explorer.

Then type:

```text
hello
add task finish report
show tasks
ask ai plan my day
```

## 12. Final note

YAM is designed to function as a practical AI assistant that remains usable even without cloud services. It is intended to be flexible, safe, and easy to extend.
