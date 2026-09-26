# YAM AI Assistant Workflow

This document explains the full workflow of the YAM AI Assistant from startup to advanced usage.

## 1. Startup workflow

1. The user launches the app.
2. `AI_YAM/AI_YAM.py` starts.
3. The banner displays the assistant name and creator credit.
4. The assistant loads environment variables.
5. It checks for required resources such as memory and Excel commands.
6. It creates default resource files if they do not exist.
7. The GUI or terminal mode starts.

## 2. Initialization workflow

During initialization, the project does the following:

- loads `.env` values if present
- builds the local fallback AI backend
- initializes the voice engine if available
- initializes the microphone if available
- loads task and note memory from JSON
- loads command data from the Excel sheet if present

## 3. User interaction flow

When the user gives input, the system performs this flow:

1. Receive user command
2. Normalize and lowercase the text
3. Match against built-in triggers and command patterns
4. Execute the matching action
5. Speak the response or show it in the interface
6. Save any changes such as tasks or notes

## 4. Command categories

The assistant handles several categories of commands:

### General conversation
- greetings
- mood checks
- thanks
- goodbye

### Utility commands
- time
- date
- note saving
- note listing
- task adding
- task listing
- task completion

### Search and web actions
- open google
- open youtube
- search web
- Wikipedia search and summary
- weather lookup
- open camera and Windows settings

### AI commands
- ask ai
- smart plan
- daily brief
- summarize notes

### Output commands
- text to speech
- audio to text
- prompt-card creation

### System actions
- shutdown
- restart
- lock workstation
- empty recycle bin

## 5. Task workflow

### Add task

1. User says: `add task prepare presentation`
2. Assistant extracts the task text.
3. It stores the task in memory.
4. It saves to the JSON memory file.
5. It confirms success.

### Complete task

1. User says: `complete task 1` (task numbers start at 1).
2. The system finds the task by index.
3. It marks it as done.
4. It saves the updated task list.

### Show tasks

1. User says: `show tasks`
2. Assistant reads pending tasks from memory.
3. It speaks or prints them to the user.

## 6. Notes workflow

1. User says: `remember project meeting at 5 pm`
2. Assistant stores it in memory.
3. The memory JSON file is updated.
4. User can later say: `show my notes`
5. Assistant reads the latest notes and responds.

## 7. AI workflow

The AI workflow is:

1. User enters a prompt.
2. The assistant builds the request.
3. It tries the configured cloud chat API if a key is available.
4. If not, it uses a limited rules-based local reply.
5. The response is returned.
6. The assistant logs the chat exchange.

## 8. Speech workflow

### Live voice input in the desktop app

1. The user clicks **Push to Talk**.
2. The UI shows `MIC ON | SPEAK NOW` and captures one phrase; no wake word is required.
3. The user speaks one command and pauses briefly.
4. The assistant transcribes and executes the command, displays the request and reply in chat, and speaks the reply.
5. The UI returns to `MIC READY | PRESS TO TALK` after processing.
6. If microphone capture fails, the UI focuses typed input. If speech output fails, the text reply remains visible and the UI reports the reason.
7. Command recognition uses an online service with an offline fallback; typed input remains available.

### Text to audio

1. User requests audio conversion.
2. Assistant accepts the text.
3. It tries `gTTS` if available.
4. If not, it falls back to `pyttsx3`.
5. File is saved to the configured output path.

### Audio to text

1. User provides an audio file path.
2. Assistant checks recognition availability.
3. It reads the file with `SpeechRecognition`.
4. It uses Google recognition if available.
5. It returns the transcription.

## 9. Camera, settings, and Wikipedia

- `open camera` launches the Windows Camera app; camera access is controlled by Windows privacy permissions.
- `open settings`, `open camera settings`, and `open sound settings` open the matching Windows Settings page.
- `search wikipedia for Saturn` and `look up Ada Lovelace on Wikipedia` search Wikipedia and speak a short page summary. Internet access is required.

## 10. Prompt-card workflow

1. User requests: `generate image ...`.
2. Assistant extracts the prompt.
3. It checks whether Pillow is installed.
4. It creates a styled card and writes the prompt on it.
5. It saves the card in the resources folder. This is not text-to-image model generation.

## 11. GUI workflow

When the desktop GUI is used:

1. Tkinter window opens.
2. Chat panel shows messages.
3. User types requests in the entry box.
4. A background thread processes the command.
5. Status bar updates to show progress.
6. Dashboard shows notes, tasks, provider, and model info.

## 12. Safety workflow

The assistant includes protective logic for risky tasks:

- shutdown requires confirmation
- restart requires confirmation
- lock workstation requires confirmation
- recycle bin clean-up requires confirmation

This prevents accidental destructive actions.

## 13. Example real project flow

```text
User: hello
YAM: Hello! I am YAM, your AI assistant.

User: add task prepare presentation
YAM: Task added.

User: remember meeting at 5 pm
YAM: I have saved that note.

User: daily brief
YAM: Provides note and task summary.

User: ask ai plan my day
YAM: Returns a practical plan.

User: generate image futuristic city skyline
YAM: Creates a prompt card file.
```

## 14. Best operating practices

- keep your virtual environment active
- use `.env` for API keys
- keep dependencies installed
- run in a terminal if you need error details
- use keyboard input when microphone support is unavailable

## 15. Summary

The YAM workflow is designed to be simple, practical, and resilient. It starts as a local helper, expands into an AI assistant, manages your tasks and notes, handles voice and text commands, and can integrate with cloud AI when configured.
