"""YAM, a desktop voice assistant with optional cloud AI integrations."""

import os
import json
import re
import ast
import math
import queue
import random
import subprocess
import sys
import webbrowser
import datetime
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlencode

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # pragma: no cover
    tk = None
    ttk = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover
    gTTS = None

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

try:
    import pyttsx3
except ImportError:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover
    sr = None

try:
    import wikipedia
except ImportError:  # pragma: no cover
    wikipedia = None

try:
    import pyjokes
except ImportError:  # pragma: no cover
    pyjokes = None

try:
    from openpyxl import Workbook, load_workbook
except ImportError:  # pragma: no cover
    Workbook = None
    load_workbook = None

try:
    import winshell
except ImportError:  # pragma: no cover
    winshell = None

try:
    import ctypes
    if os.name != "nt":
        ctypes = None
except Exception:  # pragma: no cover
    ctypes = None


BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
RESOURCES_DIR = BASE_DIR / "resources"
EXCEL_PATH = RESOURCES_DIR / "commands.xlsx"
MEMORY_PATH = RESOURCES_DIR / "memory.json"


def load_env_file(env_path=None):
    candidate_paths = []
    if env_path is not None:
        candidate_paths.append(Path(env_path))
    candidate_paths.append(BASE_DIR / ".env")
    candidate_paths.append(BASE_DIR.parent / ".env")

    for path in candidate_paths:
        if not path or not path.exists():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip() or line.strip().startswith("#") or "=" not in line:
                    continue
                key, value = [part.strip() for part in line.split("=", 1)]
                if key and not os.getenv(key):
                    os.environ[key] = value.strip().strip('"').strip("'")
        except Exception:
            continue


def print_banner():
    banner = r"""
    ███╗   ███╗██╗   ██╗███████╗
    ████╗ ████║██║   ██║██╔════╝
    ██╔████╔██║██║   ██║███████╗
    ██║╚██╔╝██║██║   ██║╚════██║
    ██║ ╚═╝ ██║╚██████╔╝███████║
    ╚═╝     ╚═╝ ╚═════╝ ╚══════╝
                YAM
         Created by MVS
    """
    print(banner)


class NeuralAIConnector:
    """Optional adapter for cloud or local neural-model providers."""

    def __init__(self):
        load_env_file()
        self.model = os.getenv("YAM_AI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("YAM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = (
            os.getenv("YAM_API_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        )
        self.provider = (
            os.getenv("YAM_AI_PROVIDER")
            or ("openai-compatible" if self.api_key else "local-fallback")
        )
        if not self.api_key:
            self.provider = "local-fallback"

    def _build_local_response(self, prompt):
        normalized = prompt.strip().lower()
        if re.search(r"\b(?:hello|hi|hey)\b", normalized):
            return "Hello! I am YAM, your AI assistant. How can I support you today?"
        if "plan" in normalized or "schedule" in normalized:
            return "Here is a practical plan: define the goal, break it into steps, assign priorities, track blockers, and review progress at the end of the day."
        if "summary" in normalized or "summarize" in normalized:
            return "The key idea is to condense the main points, preserve important facts, and remove repeated or low-value details."
        if "image" in normalized and ("generate" in normalized or "create" in normalized):
            return "I can help generate a visual concept. Please describe the scene, style, colors, subject, and mood, and I will turn that into a ready-to-use prompt."
        if "task" in normalized or "todo" in normalized:
            return "A strong task plan is: define the result, list only the critical actions, set priorities, and review completion before finishing."
        return (
            "I am YAM, your voice assistant. "
            "I can help with searches, reminders, planning, image prompts, task management, notes, and more."
        )

    def generate_text(self, prompt):
        if self.api_key and self.provider != "local-fallback":
            if openai is not None:
                try:
                    client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are YAM, a capable AI assistant for productivity, planning, and general tasks."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=220,
                    )
                    text = response.choices[0].message.content.strip()
                    if text:
                        return text
                except Exception:
                    pass

            if requests is not None:
                try:
                    payload = {
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are YAM, a capable AI assistant for productivity, planning, and general tasks."},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 220,
                    }
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    }
                    url = self.base_url.rstrip("/") + "/chat/completions"
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    if response.ok:
                        data = response.json()
                        text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        if text:
                            return text
                except Exception:
                    pass

        return self._build_local_response(prompt)

    def create_prompt_card(self, prompt, output_path):
        if Image is None:
            raise RuntimeError("Pillow is not installed")

        width, height = 1280, 720
        image = Image.new("RGB", (width, height), color=(18, 24, 42))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=28, fill=(38, 65, 98))

        title = "YAM AI Art"
        draw.text((70, 90), title, fill=(255, 255, 255), font=None)
        wrapped = self.wrap_text(prompt, 34)
        y = 180
        for line in wrapped:
            draw.text((70, y), line, fill=(180, 210, 255), font=None)
            y += 38

        image.save(output_path)
        return output_path

    @staticmethod
    def wrap_text(text, max_chars):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines[:6]


class YAMAssistant:
    def __init__(self):
        self.engine = None
        self.recognizer = None
        self.microphone = None
        self.command_data = self.default_commands()
        self.memory = self.load_memory()
        self.chat_history = []
        self.last_response = ""
        self.last_speech_error = ""
        self._microphone_calibrated = False
        self._speech_queue = queue.Queue()
        self.speech_ready = threading.Event()
        self.speech_error = ""
        self.neural = NeuralAIConnector()

        if pyttsx3 is not None:
            threading.Thread(target=self._speech_worker, daemon=True).start()
        else:
            self.speech_error = "pyttsx3 is not installed"
            self.speech_ready.set()

        if sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.operation_timeout = 8
                self.microphone = sr.Microphone()
            except Exception as exc:  # pragma: no cover
                print(f"Microphone init failed: {exc}")
                self.recognizer = None
                self.microphone = None

        self.ensure_resources()
        self.load_commands_from_excel()

    def _speech_worker(self):
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
            self.engine.setProperty("rate", 170)
            self.engine.setProperty("volume", 0.9)
        except Exception as exc:  # pragma: no cover
            self.speech_error = str(exc)
            print(f"Voice engine init failed: {exc}")
        finally:
            self.speech_ready.set()

        while True:
            request = self._speech_queue.get()
            if request is None:
                return

            completion, result = request["completion"], request["result"]
            try:
                if self.engine is None:
                    result["error"] = "Voice output is unavailable."
                elif request["action"] == "speak":
                    self.engine.say(request["text"])
                    self.engine.runAndWait()
                else:
                    self.engine.save_to_file(request["text"], request["path"])
                    self.engine.runAndWait()
                    result["path"] = request["path"]
            except Exception as exc:  # pragma: no cover
                result["error"] = str(exc)
            finally:
                completion.set()

    @staticmethod
    def default_commands():
        return {
            "greetings": {
                "triggers": ["hello", "hi", "hey", "good morning", "good evening", "greetings"],
                "responses": [
                    "Hello sir! How may I help you today?",
                    "Hi there! I am ready to assist you.",
                    "Hey! What can I do for you?",
                    "Greetings! I am YAM, your assistant."
                ],
            },
            "mood": {
                "triggers": ["how are you", "how are you doing", "how do you feel"],
                "responses": [
                    "I am doing very well, thank you.",
                    "I am excellent and ready to help.",
                    "All systems are operational."
                ],
            },
            "thanks": {
                "triggers": ["thank you", "thanks"],
                "responses": [
                    "You are welcome, sir.",
                    "It is my pleasure to help you.",
                    "Always happy to assist."
                ],
            },
            "goodbye": {
                "triggers": ["bye", "goodbye", "see you later", "exit"],
                "responses": [
                    "Goodbye sir. Have a great day.",
                    "Take care. I will be here whenever you need me.",
                    "Until next time."
                ],
            }
        }

    def ensure_resources(self):
        RESOURCES_DIR.mkdir(exist_ok=True)
        if not EXCEL_PATH.exists():
            self.create_default_excel_file()
        if not MEMORY_PATH.exists():
            MEMORY_PATH.write_text(json.dumps({"notes": [], "tasks": []}, indent=2), encoding="utf-8")

    def load_memory(self):
        try:
            if MEMORY_PATH.exists():
                with MEMORY_PATH.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        notes = data.get("notes", [])
                        tasks = data.get("tasks", [])
                        data["notes"] = [str(note) for note in notes if note is not None] if isinstance(notes, list) else []
                        data["tasks"] = [task for task in tasks if isinstance(task, dict)] if isinstance(tasks, list) else []
                        return data
        except Exception:
            pass
        return {"notes": [], "tasks": []}

    def save_memory(self):
        try:
            with MEMORY_PATH.open("w", encoding="utf-8") as file:
                json.dump(self.memory, file, indent=2)
        except Exception as exc:
            print(f"Memory save failed: {exc}")

    def create_default_excel_file(self):
        if Workbook is None:
            print("openpyxl is not available; continuing without Excel command file.")
            return

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Commands"
        sheet.append(["Category", "Trigger", "Response"])
        sheet.append(["greetings", "hello", "Hello sir! How may I help you today?"])
        sheet.append(["greetings", "hi", "Hi there! I am ready to assist you."])
        sheet.append(["mood", "how are you", "I am doing very well, thank you."])
        sheet.append(["thanks", "thank you", "You are welcome, sir."])
        sheet.append(["goodbye", "goodbye", "Goodbye sir. Have a great day."])

        workbook.save(EXCEL_PATH)
        print(f"Created default command file: {EXCEL_PATH}")

    def load_commands_from_excel(self):
        if load_workbook is None or not EXCEL_PATH.exists():
            return

        try:
            workbook = load_workbook(EXCEL_PATH, read_only=True)
            if "Commands" not in workbook.sheetnames:
                workbook.close()
                return

            worksheet = workbook["Commands"]
            data = {}

            for row in worksheet.iter_rows(min_row=2, max_col=3, values_only=True):
                category, trigger, response = row
                if not category:
                    continue
                category_key = str(category).strip().lower()
                data.setdefault(category_key, {"triggers": [], "responses": []})

                if trigger and response:
                    data[category_key]["triggers"].append(str(trigger).strip().lower())
                    data[category_key]["responses"].append(str(response).strip())

            workbook.close()
            if data:
                self.command_data = data
                print("Excel commands loaded successfully.")
        except Exception as exc:  # pragma: no cover
            print(f"Could not load Excel commands: {exc}")

    def speak(self, text):
        if not text:
            return False

        self.last_response = str(text).strip()
        self.last_speech_error = ""
        print(f"YAM: {text}")
        if pyttsx3 is None:
            self.last_speech_error = self.speech_error or "Voice output is unavailable."
            return False

        if not self.speech_ready.wait(timeout=10):
            self.last_speech_error = "Voice engine initialization timed out."
            return False
        if self.engine is None:
            self.last_speech_error = self.speech_error or "Voice engine failed to initialize."
            return False

        completion = threading.Event()
        result = {}
        self._speech_queue.put({"action": "speak", "text": str(text), "completion": completion, "result": result})
        if not completion.wait(timeout=30):  # pragma: no cover
            self.last_speech_error = "Speech output timed out."
        elif result.get("error"):
            self.last_speech_error = result["error"]
        if self.last_speech_error:
            print(f"Speech output failed: {self.last_speech_error}")
            return False
        return True

    def get_system_snapshot(self):
        tasks = self.memory.get("tasks", [])
        notes = self.memory.get("notes", [])
        pending = sum(1 for item in tasks if not item.get("done", False))
        return {
            "notes": len(notes),
            "tasks": len(tasks),
            "pending_tasks": pending,
            "ai_provider": self.neural.provider,
            "ai_model": self.neural.model,
            "api_key_configured": bool(self.neural.api_key),
        }

    def add_chat_message(self, role, text):
        if not text:
            return
        self.chat_history.append({"role": role, "content": str(text).strip()})
        if len(self.chat_history) > 30:
            self.chat_history = self.chat_history[-30:]

    def ask_ai(self, prompt, system_prompt=None):
        if not prompt or not str(prompt).strip():
            return "Please provide a prompt for the AI."

        user_prompt = str(prompt).strip()
        self.add_chat_message("user", user_prompt)

        final_prompt = user_prompt
        if system_prompt:
            final_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = self.neural.generate_text(final_prompt)
        self.add_chat_message("assistant", response)
        return response

    def summarize_notes(self):
        notes = self.memory.get("notes", [])
        if not notes:
            return "There are no notes saved yet."
        if not self.neural.api_key or self.neural.provider == "local-fallback":
            return "Here are your recent notes: " + "; ".join(notes[-5:])
        note_text = "\n".join(notes)
        return self.ask_ai(note_text, system_prompt="Summarize these notes for me in a clear, concise way.")

    def add_task(self, task, priority="normal"):
        task_text = str(task).strip()
        if not task_text:
            return False
        self.memory.setdefault("tasks", [])
        self.memory["tasks"].append({
            "task": task_text,
            "priority": str(priority).strip().lower() or "normal",
            "done": False,
            "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        self.save_memory()
        return True

    def complete_task(self, task_index=None):
        tasks = self.memory.get("tasks", [])
        if not tasks:
            return False

        if task_index is None:
            for idx, item in enumerate(tasks):
                if not item.get("done", False):
                    item["done"] = True
                    self.save_memory()
                    return True
            return False

        try:
            idx = int(task_index)
        except (TypeError, ValueError):
            return False

        if 1 <= idx <= len(tasks):
            tasks[idx - 1]["done"] = True
            self.save_memory()
            return True
        return False

    def show_tasks(self):
        tasks = self.memory.get("tasks", [])
        if not tasks:
            return []
        return tasks

    def search_web(self, query):
        search_query = str(query).strip()
        if not search_query:
            return "Please provide a search query."
        url = "https://www.google.com/search?" + urlencode({"q": search_query})
        try:
            webbrowser.open(url)
            return f"Searching the web for: {search_query}"
        except Exception as exc:
            return f"Web search failed: {exc}"

    def search_wikipedia(self, query):
        search_query = str(query).strip()
        if not search_query:
            return "Please provide a Wikipedia search topic."
        if wikipedia is None:
            return "Wikipedia search is unavailable because its package is not installed."

        try:
            results = wikipedia.search(search_query, results=3)
            if not results:
                return f"Wikipedia did not find a page for {search_query}."
            title = results[0]
            summary = wikipedia.summary(title, sentences=2, auto_suggest=False)
            return f"Wikipedia: {title}. {summary}"
        except wikipedia.exceptions.DisambiguationError as exc:
            choices = ", ".join(exc.options[:5])
            return f"That topic is ambiguous. Wikipedia suggests: {choices}."
        except wikipedia.exceptions.PageError:
            return f"Wikipedia could not find a page for {search_query}."
        except Exception as exc:
            return f"Wikipedia search failed: {exc}"

    @staticmethod
    def open_windows_target(target, label):
        if os.name != "nt" or not hasattr(os, "startfile"):
            return f"Opening {label} is only supported on Windows."
        try:
            os.startfile(target)
            return f"Opening {label}."
        except OSError as exc:
            return f"I could not open {label}: {exc}"

    def daily_brief(self):
        now = datetime.datetime.now()
        notes = self.memory.get("notes", [])
        tasks = self.memory.get("tasks", [])
        pending = [item.get("task") for item in tasks if not item.get("done", False)]
        notes_summary = "; ".join(notes[-3:]) if notes else "No notes saved yet."
        tasks_summary = "; ".join(pending[:3]) if pending else "No pending tasks."
        return (
            f"Good {('morning', 'afternoon', 'evening')[0 if now.hour < 12 else 1 if now.hour < 18 else 2]}! "
            f"Today is {now.strftime('%A, %B %d, %Y')}. "
            f"Recent notes: {notes_summary}. "
            f"Pending tasks: {tasks_summary}."
        )

    def smart_plan(self, goal=None):
        tasks = self.memory.get("tasks", [])
        notes = self.memory.get("notes", [])
        pending = [item.get("task") for item in tasks if not item.get("done", False)]
        objective = str(goal).strip() if goal else "the current priority goal"
        if not pending and not notes:
            return (
                f"Plan for {objective}: 1) define the outcome, 2) break it into 3 small actions, 3) set a 30-minute focus block, "
                "4) review progress and adjust once complete."
            )
        task_list = "; ".join(pending[:3]) if pending else "review your saved notes"
        note_hint = "; ".join(notes[-2:]) if notes else "keep momentum with one focused action"
        return (
            f"Smart plan for {objective}: 1) start with the highest priority task: {task_list}; "
            f"2) use the recent notes to guide execution: {note_hint}; 3) work in focused time blocks; "
            "4) finish by summarizing outcomes and updating the task list."
        )

    def launch_app(self, app_name):
        app = str(app_name).strip().lower()
        targets = {
            "chrome": "https://www.google.com",
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "edge": "https://www.microsoft.com",
            "calculator": "calc",
            "notepad": "notepad",
            "explorer": "explorer",
            "cmd": "cmd",
            "terminal": "cmd",
        }

        if app in targets:
            target = targets[app]
            if target.startswith("http"):
                webbrowser.open(target)
                return f"Opening {app}."
            try:
                os.startfile(target)
                return f"Opening {app}."
            except Exception as exc:
                return f"I could not open {app}: {exc}"

        try:
            os.startfile(app)
            return f"Opening {app}."
        except Exception:
            return f"I could not open {app}."

    def text_to_audio(self, text, output_file=None):
        if not text:
            return None

        if output_file is None:
            output_file = Path(tempfile.gettempdir()) / "yam_audio.mp3"

        if gTTS is not None:
            try:
                tts = gTTS(text=text, lang="en")
                tts.save(str(output_file))
                return str(output_file)
            except Exception as exc:
                print(f"gTTS failed: {exc}")

        if pyttsx3 is not None:
            completion = threading.Event()
            result = {}
            self._speech_queue.put({
                "action": "save",
                "text": text,
                "path": str(output_file),
                "completion": completion,
                "result": result,
            })
            if completion.wait(timeout=30) and result.get("path"):
                return result["path"]
            if result.get("error"):
                print(f"pyttsx3 save_to_file failed: {result['error']}")

        return None

    def audio_to_text(self, audio_file):
        if self.recognizer is None:
            return "Speech recognition is not available on this system."

        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
                return self.recognizer.recognize_google(audio_data)
        except Exception as exc:
            return f"Audio transcription failed: {exc}"

    def create_prompt_card(self, prompt, output_file=None):
        if output_file is None:
            output_file = RESOURCES_DIR / "prompt_card.png"

        if Image is None:
            raise RuntimeError("Pillow is required to create a prompt card")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return self.neural.create_prompt_card(prompt, str(output_path))

    def smart_reply(self, prompt):
        if not prompt:
            return "I am ready to help you."
        return self.neural.generate_text(prompt)

    def listen_for_text(self, timeout=8, phrase_time_limit=5, status_callback=None, recognition_keywords=None):
        if self.recognizer is None or self.microphone is None:
            raise RuntimeError("No microphone is available")

        try:
            with self.microphone as source:
                if not self._microphone_calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self._microphone_calibrated = True
                if status_callback is not None:
                    status_callback("MIC ON | CAPTURING")
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
        except Exception as exc:
            self._microphone_calibrated = False
            raise RuntimeError(f"Microphone capture failed: {exc}") from exc

        if status_callback is not None:
            status_callback("MIC ON | RECOGNIZING")
        if recognition_keywords:
            recognized_text = ""
            try:
                recognized_text = self.recognizer.recognize_google(audio).lower()
                if re.match(r"^(?:hey\s+)?(?:wake\s+)?up\b", recognized_text.strip()):
                    return recognized_text
            except (sr.UnknownValueError, sr.RequestError):
                pass
            try:
                offline_text = self.recognizer.recognize_sphinx(audio).lower()
                if re.match(r"^(?:hey\s+)?(?:wake\s+)?up\b", offline_text.strip()):
                    return offline_text
            except Exception:
                offline_text = ""
            if recognized_text:
                return recognized_text
            if offline_text:
                return offline_text
            try:
                return self.recognizer.recognize_sphinx(
                    audio,
                    keyword_entries=[(word, 1e-20) for word in recognition_keywords],
                ).lower()
            except Exception:
                return ""
        try:
            online_text = self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            try:
                return self.recognizer.recognize_sphinx(
                    audio,
                    keyword_entries=[(word, 1e-20) for word in recognition_keywords] if recognition_keywords else None,
                ).lower()
            except Exception:
                return ""
        except sr.RequestError as exc:
            try:
                return self.recognizer.recognize_sphinx(
                    audio,
                    keyword_entries=[(word, 1e-20) for word in recognition_keywords] if recognition_keywords else None,
                ).lower()
            except Exception as fallback_exc:
                raise RuntimeError(f"Speech recognition failed: {exc}") from fallback_exc

        known_short_commands = {"hi", "hello", "hey", "google", "calculator", "notepad", "joke", "help", "time", "date"}
        if len(online_text.split()) == 1 and online_text not in known_short_commands:
            try:
                offline_text = self.recognizer.recognize_sphinx(audio).lower()
                if len(offline_text.split()) > len(online_text.split()):
                    return offline_text
            except Exception:
                pass
        return online_text

    def process_command(self, command):
        if not command:
            return False

        text = command.strip().lower()

        for category, details in self.command_data.items():
            for trigger in details.get("triggers", []):
                if re.search(rf"(?<!\w){re.escape(trigger)}(?!\w)", text):
                    response = random.choice(details.get("responses", ["I heard you."]))
                    self.speak(response)
                    if category == "goodbye":
                        raise SystemExit
                    return True

        if re.search(r"\btime\b", text):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}.")
            return True

        if "smart plan" in text or "plan my day" in text or "make a plan" in text:
            goal = text.replace("smart plan", "").replace("plan my day", "").replace("make a plan", "").strip()
            if not goal:
                goal = "your day"
            self.speak(self.smart_plan(goal))
            return True

        if re.search(r"\bdate\b|\btoday\b|\bwhat day\b", text):
            today = datetime.datetime.now()
            self.speak(f"Today is {today.strftime('%A')}, {today.strftime('%B %d, %Y')}.")
            return True

        if "your name" in text:
            self.speak("I am YAM, your voice assistant.")
            return True

        wikipedia_match = re.match(
            r"^(?:search(?:\s+for)?(?:\s+on)?\s+wikipedia(?:\s+for)?|wikipedia)\s+(.+)$",
            text,
        )
        if wikipedia_match:
            self.speak(self.search_wikipedia(wikipedia_match.group(1)))
            return True

        wikipedia_suffix = re.match(r"^look up\s+(.+?)\s+on wikipedia$", text)
        if wikipedia_suffix:
            self.speak(self.search_wikipedia(wikipedia_suffix.group(1)))
            return True

        settings_targets = {
            "open camera settings": ("ms-settings:privacy-webcam", "camera privacy settings"),
            "open display settings": ("ms-settings:display", "display settings"),
            "open sound settings": ("ms-settings:sound", "sound settings"),
            "open settings": ("ms-settings:", "Windows Settings"),
            "settings": ("ms-settings:", "Windows Settings"),
        }
        if text in settings_targets:
            target, label = settings_targets[text]
            self.speak(self.open_windows_target(target, label))
            return True

        if text in {"open camera", "launch camera", "camera"}:
            self.speak(self.open_windows_target("microsoft.windows.camera:", "Camera"))
            return True

        if text in {"google", "open google"} or text.startswith("open google "):
            webbrowser.open("https://www.google.com")
            self.speak("Opening Google.")
            return True

        if "open youtube" in text:
            webbrowser.open("https://www.youtube.com")
            self.speak("Opening YouTube.")
            return True

        if text in {"calculator", "open calculator"}:
            try:
                os.startfile("calc")
                self.speak("Opening calculator.")
            except Exception:
                self.speak("I could not open calculator on this system.")
            return True

        if text in {"notepad", "open notepad"}:
            try:
                os.startfile("notepad")
                self.speak("Opening notepad.")
            except Exception:
                self.speak("I could not open notepad on this system.")
            return True

        if "add task" in text or "new task" in text:
            query = text.replace("add task", "").replace("new task", "").strip()
            if not query:
                self.speak("Please tell me the task to save.")
                return True
            added = self.add_task(query)
            if added:
                self.speak(f"Task added: {query}.")
            else:
                self.speak("I could not save that task.")
            return True

        if "complete task" in text or "finish task" in text:
            match = re.search(r"(?:complete|finish) task\s*(\d+)?", text)
            index = int(match.group(1)) if match and match.group(1) else None
            success = self.complete_task(index)
            if success:
                self.speak("Task marked as completed.")
            else:
                self.speak("That task number was not found. Use the number shown in your task list.")
            return True

        if "show tasks" in text or "list tasks" in text or "my tasks" in text:
            tasks = self.show_tasks()
            if not tasks:
                self.speak("You do not have any saved tasks.")
            else:
                pending = [
                    f"Task {idx + 1}: {item.get('task')}"
                    for idx, item in enumerate(tasks)
                    if not item.get("done", False)
                ]
                if not pending:
                    self.speak("All tasks are completed.")
                else:
                    self.speak("Your pending tasks are: " + "; ".join(pending[:5]))
            return True

        if text.startswith("search for ") or text.startswith("search web "):
            query = text.replace("search for", "").replace("search web", "").strip()
            if not query:
                self.speak("Please provide a search query.")
                return True
            response = self.search_web(query)
            self.speak(response)
            return True

        if "ask ai" in text or "ai chat" in text or "chat with ai" in text:
            prompt = text.replace("ask ai", "").replace("ai chat", "").replace("chat with ai", "").strip()
            if not prompt:
                self.speak("Please tell me what you want the AI to help with.")
                return True
            response = self.ask_ai(prompt)
            self.speak(response)
            return True

        if "summarize notes" in text or "summary of notes" in text:
            self.speak(self.summarize_notes())
            return True

        if "daily brief" in text or "brief me" in text:
            self.speak(self.daily_brief())
            return True

        if "open app" in text or "launch app" in text:
            app_name = text.replace("open app", "").replace("launch app", "").strip()
            if not app_name:
                self.speak("Please provide the app name to open.")
                return True
            self.speak(self.launch_app(app_name))
            return True

        if "generate image" in text or "create image" in text:
            prompt = text.replace("generate image", "").replace("create image", "").strip()
            if not prompt:
                self.speak("Please provide an image prompt.")
                return True
            path = RESOURCES_DIR / "prompt_card.png"
            try:
                result = self.create_prompt_card(prompt, path)
                self.speak(f"Prompt card created at {result}.")
            except Exception as exc:
                self.speak(f"Prompt card creation failed: {exc}")
            return True

        if "text to speech" in text or "convert text to audio" in text or "tts" in text:
            prompt = text.replace("text to speech", "").replace("convert text to audio", "").replace("tts", "").strip()
            if not prompt:
                self.speak("Please provide the text to convert into speech.")
                return True
            output = self.text_to_audio(prompt, RESOURCES_DIR / "voice_output.mp3")
            if output:
                self.speak(f"Audio file created at {output}.")
            else:
                self.speak("Audio conversion is unavailable in this environment.")
            return True

        if "audio to text" in text or "transcribe" in text:
            match = re.search(r"(?:audio to text|transcribe)\s+(.+)", text)
            audio_path = match.group(1).strip() if match else str(RESOURCES_DIR / "voice_input.wav")
            if os.path.exists(audio_path):
                transcript = self.audio_to_text(audio_path)
                self.speak(transcript)
            else:
                self.speak("I could not find that audio file. Please provide a valid path.")
            return True

        if "calculate" in text or "compute" in text or "what is" in text and any(op in text for op in ["+","-","*","/","%","(",")"]):
            expr = re.sub(r"[^0-9+\-*/%().\s]", "", text)
            expr = expr.replace("what is", "").replace("calculate", "").replace("compute", "").strip()
            if expr:
                try:
                    safe_expr = ast.parse(expr, mode="eval")
                    allowed_names = {"__builtins__": {}, "math": math}
                    value = eval(compile(safe_expr, "<calc>", "eval"), allowed_names, {})
                    self.speak(f"The result is {value}.")
                    return True
                except Exception:
                    self.speak("I could not calculate that expression.")
                    return True

        if "what do you remember" in text or "show my notes" in text or "list notes" in text:
            notes = self.memory.get("notes", [])
            if not notes:
                self.speak("I do not have any saved notes yet.")
            else:
                summary = "; ".join(notes[-5:])
                self.speak(f"Your recent notes are: {summary}.")
            return True

        note_match = re.match(r"^(?:remember|save note|take a note|note)(?:\s+that)?\s*(.*)$", text)
        if note_match:
            note_text = note_match.group(1).strip()
            if not note_text:
                self.speak("What should I remember?")
                return True
            self.memory.setdefault("notes", []).append(note_text)
            self.save_memory()
            self.speak("I have saved that note.")
            return True

        if "weather" in text:
            if requests is not None:
                try:
                    response = requests.get("https://wttr.in/?format=3", timeout=5)
                    if response.ok:
                        self.speak(response.text.strip())
                        return True
                except Exception:
                    pass
            self.speak("Weather service is unavailable right now.")
            return True

        if "who is" in text or "what is" in text:
            topic = text.replace("who is", "").replace("what is", "").strip()
            if wikipedia is not None and topic:
                try:
                    summary = wikipedia.summary(topic, sentences=2)
                    self.speak(summary)
                    return True
                except Exception:
                    pass
            self.speak("I could not find that information right now.")
            return True

        if "joke" in text:
            if pyjokes is not None:
                self.speak(pyjokes.get_joke())
            else:
                self.speak("Why did the scarecrow win an award? Because he was outstanding in his field.")
            return True

        if re.search(r"\block\b", text) and re.search(r"\b(?:window|computer|workstation)\b", text):
            if "confirm lock" not in text:
                self.speak("Please confirm by saying 'confirm lock computer'.")
                return True
            if ctypes is not None:
                ctypes.windll.user32.LockWorkStation()
                self.speak("Locking the computer.")
            else:
                self.speak("This feature is available only on Windows.")
            return True

        if "shutdown" in text:
            if "confirm shutdown" not in text:
                self.speak("Please confirm shutdown by saying 'confirm shutdown'.")
                return True
            self.speak("Shutting down the system.")
            if os.name == "nt":
                subprocess.call("shutdown /s /t 1", shell=True)
            return True

        if "restart" in text:
            if "confirm restart" not in text:
                self.speak("Please confirm restart by saying 'confirm restart'.")
                return True
            self.speak("Restarting the system.")
            if os.name == "nt":
                subprocess.call("shutdown /r /t 1", shell=True)
            return True

        if "empty recycle bin" in text:
            if "confirm empty recycle bin" not in text:
                self.speak("Please confirm emptying the recycle bin by saying 'confirm empty recycle bin'.")
                return True
            if winshell is not None:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                self.speak("Recycle bin emptied.")
            else:
                self.speak("Recycle bin clean-up is only supported on Windows.")
            return True

        if text in {"bye", "goodbye", "exit", "quit"}:
            self.speak("Goodbye sir.")
            raise SystemExit

        if "help" in text:
            self.speak("I can tell time, search the web, create prompt cards, convert text to speech, transcribe audio, and manage tasks and notes.")
            return True

        smart_answer = self.smart_reply(text)
        self.speak(smart_answer)
        return True

    def run(self):
        self.speak("Hello sir! I am YAM, your voice assistant.")

        while True:
            try:
                if self.recognizer is None or self.microphone is None:
                    self.speak("Voice input is unavailable. Please type your command.")
                    command = input("Type your command: ").strip()
                else:
                    command = self.listen_for_text(timeout=10, phrase_time_limit=6)
                if not command:
                    self.speak("I did not hear anything. Please type your command instead.")
                    command = input("Type your command: ").strip()
                    if not command:
                        continue
                self.process_command(command)
            except RuntimeError as exc:
                self.speak(f"Voice input failed: {exc}. Please type your command.")
                command = input("Type your command: ").strip()
                if command:
                    self.process_command(command)
            except SystemExit:
                break
            except KeyboardInterrupt:
                print("Program interrupted by user.")
                break


class YAMApp:
    """Desktop interface for YAM."""

    def __init__(self, root, assistant):
        self.root = root
        self.assistant = assistant
        self.closing = False
        self.root.title("YAM AI Assistant")
        self.root.geometry("980x680")
        self.root.minsize(820, 560)
        self.root.configure(bg="#0d1117")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.status_var = tk.StringVar(value="Ready")
        self.command_var = tk.StringVar()
        self.snapshot_var = tk.StringVar(value="")
        self.voice_state_var = tk.StringVar(
            value="MIC READY | PRESS TO TALK" if assistant.recognizer is not None and assistant.microphone is not None else "MIC UNAVAILABLE | TYPE COMMAND"
        )
        self.voice_active = False
        self.voice_stop_event = threading.Event()
        self.pending_text_command = None
        self.voice_finish_status = "Ready"
        self.ui_queue = queue.Queue()
        self.root.after(50, self.process_ui_queue)

        header = tk.Label(root, text="YAM AI Assistant", font=("Segoe UI", 22, "bold"), fg="#dfe7ff", bg="#0d1117")
        header.pack(pady=(18, 8), fill=tk.X)

        status = tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 11), fg="#7ee787", bg="#0d1117")
        status.pack(anchor="w", padx=20)

        self.voice_status = tk.Label(
            root,
            textvariable=self.voice_state_var,
            font=("Segoe UI", 10, "bold"),
            fg="#7ee787" if assistant.microphone is not None else "#f85149",
            bg="#0d1117",
        )
        self.voice_status.pack(anchor="w", padx=20, pady=(4, 0))

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(12, 10))

        self.chat_tab = tk.Frame(notebook, bg="#0d1117")
        self.dashboard_tab = tk.Frame(notebook, bg="#0d1117")
        notebook.add(self.chat_tab, text="Chat")
        notebook.add(self.dashboard_tab, text="Dashboard")

        conversation = tk.Text(self.chat_tab, bg="#111827", fg="#e5e7eb", wrap=tk.WORD, font=("Segoe UI", 11), padx=12, pady=12)
        conversation.configure(state="disabled")
        conversation.pack(fill=tk.BOTH, expand=True, padx=20, pady=(18, 10))
        self.conversation = conversation

        controls = tk.Frame(self.chat_tab, bg="#0d1117")
        controls.pack(fill=tk.X, padx=20, pady=(0, 12))

        entry = tk.Entry(controls, textvariable=self.command_var, bg="#161b22", fg="#f8fafc", insertbackground="#f8fafc", font=("Segoe UI", 11))
        entry.bind("<Return>", self.on_send)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry = entry

        send_btn = tk.Button(controls, text="Send", command=self.send_manual_command, bg="#2f81f7", fg="white", font=("Segoe UI", 10, "bold"), padx=18)
        send_btn.pack(side=tk.RIGHT)

        lower = tk.Frame(self.chat_tab, bg="#0d1117")
        lower.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.listen_button = tk.Button(
            lower,
            text="Push to Talk",
            command=self.push_to_talk,
            bg="#238636",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            state=tk.NORMAL if assistant.recognizer is not None and assistant.microphone is not None else tk.DISABLED,
        )
        self.listen_button.pack(side=tk.LEFT, padx=(0, 10))

        quick = tk.Button(lower, text="Speak Test", command=self.test_voice, bg="#1f6feb", fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        quick.pack(side=tk.LEFT, padx=(0, 10))

        quick2 = tk.Button(lower, text="Create Prompt Card", command=self.create_demo_prompt_card, bg="#7847f5", fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        quick2.pack(side=tk.LEFT, padx=(0, 10))

        quick3 = tk.Button(lower, text="Ask AI", command=self.ask_ai_chat, bg="#0ea5e9", fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        quick3.pack(side=tk.LEFT, padx=(0, 10))

        quick4 = tk.Button(lower, text="Daily Brief", command=self.daily_brief_chat, bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        quick4.pack(side=tk.LEFT, padx=(0, 10))

        quick5 = tk.Button(lower, text="Clear", command=self.clear_chat, bg="#3b4252", fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        quick5.pack(side=tk.LEFT)

        dash_frame = tk.Frame(self.dashboard_tab, bg="#0d1117")
        dash_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(dash_frame, text="System Overview", font=("Segoe UI", 16, "bold"), fg="#f8fafc", bg="#0d1117").pack(anchor="w", pady=(0, 12))
        snapshot_label = tk.Label(dash_frame, textvariable=self.snapshot_var, justify=tk.LEFT, fg="#dfe7ff", bg="#0d1117", font=("Segoe UI", 11), padx=10, pady=12)
        snapshot_label.pack(anchor="w", fill=tk.X)

        self.update_dashboard()
        self.append_chat("assistant", "YAM is ready. Ask me for a task, search, note, image, brief, or AI conversation.")

    def append_chat(self, role, message):
        self.conversation.configure(state="normal")
        prefix = "You: " if role == "user" else "YAM: "
        self.conversation.insert(tk.END, prefix + message + "\n\n")
        self.conversation.see(tk.END)
        self.conversation.configure(state="disabled")

    def schedule_ui(self, callback, *args):
        if self.closing:
            return
        self.ui_queue.put((callback, args))

    def process_ui_queue(self):
        while not self.closing:
            try:
                callback, args = self.ui_queue.get_nowait()
            except queue.Empty:
                break
            callback(*args)
        if not self.closing:
            self.root.after(50, self.process_ui_queue)

    def close(self):
        self.closing = True
        self.voice_stop_event.set()
        self.root.destroy()

    def update_status(self, msg):
        self.status_var.set(msg)

    def push_to_talk(self):
        if self.voice_active:
            return

        if self.assistant.recognizer is None or self.assistant.microphone is None:
            self.voice_state_var.set("MIC UNAVAILABLE")
            self.voice_status.configure(fg="#f85149")
            self.update_status("No microphone is available")
            return

        self.voice_stop_event.clear()
        self.voice_active = True
        self.voice_finish_status = "Ready"
        self.listen_button.configure(text="Listening...", state=tk.DISABLED, bg="#da3633")
        self.set_voice_state("MIC ON | SPEAK NOW", "#3fb950")
        self.update_status("Speak one command; YAM will process it after a short pause")
        threading.Thread(target=self.capture_push_to_talk, daemon=True).start()

    def capture_push_to_talk(self):
        finish_ui = True
        try:
            command = self.assistant.listen_for_text(
                timeout=7,
                phrase_time_limit=10,
                status_callback=self.schedule_capture_status,
            )
            if self.voice_stop_event.is_set():
                return
            if not command:
                self.voice_finish_status = "No speech detected. Press Push to Talk and try again."
                return

            self.schedule_ui(self.append_chat, "user", command)
            self.schedule_ui(self.set_voice_state, "MIC ON | PROCESSING COMMAND", "#d29922")
            self.assistant.last_response = ""
            self.assistant.last_speech_error = ""
            self.assistant.process_command(command)
            if self.assistant.last_response:
                self.schedule_ui(self.append_chat, "assistant", self.assistant.last_response)
            if self.assistant.last_speech_error:
                self.voice_finish_status = "Reply shown, but voice output failed"
                self.schedule_ui(self.show_speech_error, self.assistant.last_speech_error)
            else:
                self.voice_finish_status = "Voice command completed"
        except SystemExit:
            self.voice_stop_event.set()
            self.voice_active = False
            finish_ui = False
            self.schedule_ui(self.close)
            return
        except Exception as exc:
            self.voice_active = False
            finish_ui = False
            self.schedule_ui(self.handle_voice_error, str(exc))
            return
        finally:
            if finish_ui:
                self.schedule_ui(self.finish_voice_listening)

    def schedule_capture_status(self, text):
        color = "#d29922" if "RECOGNIZING" in text else "#3fb950"
        self.schedule_ui(self.set_voice_state, text, color)

    def handle_voice_error(self, message):
        self.voice_stop_event.set()
        self.voice_active = False
        self.listen_button.configure(text="Push to Talk", state=tk.NORMAL, bg="#238636")
        self.set_voice_state("MIC OFF | TYPE COMMAND", "#f85149")
        self.update_status("Voice input failed. Type your command below.")
        self.append_chat("assistant", f"Voice input unavailable: {message}. You can type commands below.")
        self.command_entry.focus_set()
        self.submit_pending_text_command()

    def show_speech_error(self, message):
        self.append_chat("assistant", f"Voice output failed: {message}")
        self.update_status("Reply shown, but voice output failed")

    def set_voice_state(self, text, color):
        self.voice_state_var.set(text)
        self.voice_status.configure(fg=color)

    def finish_voice_listening(self):
        self.voice_active = False
        if self.closing:
            return
        self.listen_button.configure(text="Push to Talk", state=tk.NORMAL, bg="#238636")
        self.set_voice_state("MIC READY | PRESS TO TALK", "#7ee787")
        if not self.pending_text_command:
            self.update_status(self.voice_finish_status)
        self.submit_pending_text_command()

    def submit_pending_text_command(self):
        command = self.pending_text_command
        self.pending_text_command = None
        if command:
            self.submit_text_command(command)

    def on_send(self, event=None):
        self.send_manual_command()

    def send_manual_command(self):
        text = self.command_var.get().strip()
        if not text:
            return
        if self.voice_active:
            self.command_var.set("")
            self.pending_text_command = text
            self.voice_stop_event.set()
            self.update_status("Stopping microphone before processing typed command...")
            return
        self.command_var.set("")
        self.submit_text_command(text)

    def submit_text_command(self, text):
        self.append_chat("user", text)
        self.update_status("Processing request...")

        def worker():
            try:
                self.assistant.last_response = ""
                self.assistant.last_speech_error = ""
                result = self.assistant.process_command(text)
                if self.assistant.last_response:
                    self.schedule_ui(self.append_chat, "assistant", self.assistant.last_response)
                if self.assistant.last_speech_error:
                    self.schedule_ui(self.show_speech_error, self.assistant.last_speech_error)
                elif result:
                    self.schedule_ui(self.update_status, "Completed")
                else:
                    self.schedule_ui(self.update_status, "Waiting for input")
            except SystemExit:
                self.schedule_ui(self.close)
            except Exception as exc:
                self.schedule_ui(self.append_chat, "assistant", f"System error: {exc}")
                self.schedule_ui(self.update_status, "Error")

        threading.Thread(target=worker, daemon=True).start()

    def test_voice(self):
        self.append_chat("assistant", "Testing voice output...")
        self.update_status("Testing voice output...")

        def worker():
            if self.assistant.speak("Voice system active. YAM is online."):
                self.schedule_ui(self.update_status, "Voice test successful")
            else:
                self.schedule_ui(self.show_speech_error, self.assistant.last_speech_error)

        threading.Thread(target=worker, daemon=True).start()

    def create_demo_prompt_card(self):
        self.append_chat("assistant", "Creating a prompt card...")
        try:
            output = self.assistant.create_prompt_card("futuristic robot city skyline with neon lights", RESOURCES_DIR / "yam_gui_demo.png")
            self.append_chat("assistant", f"Prompt card saved at: {output}")
            self.update_status("Prompt card ready")
        except Exception as exc:
            self.append_chat("assistant", f"Prompt card creation failed: {exc}")
            self.update_status("Prompt card error")

    def clear_chat(self):
        self.conversation.configure(state="normal")
        self.conversation.delete("1.0", tk.END)
        self.conversation.configure(state="disabled")
        self.append_chat("assistant", "Conversation cleared. YAM is ready for the next task.")

    def update_dashboard(self):
        data = self.assistant.get_system_snapshot()
        status = (
            f"Notes: {data['notes']} | Tasks: {data['tasks']} | Pending: {data['pending_tasks']} | "
            f"AI Provider: {data['ai_provider']} | Model: {data['ai_model']} | API Key: {'yes' if data['api_key_configured'] else 'no'}"
        )
        self.snapshot_var.set(status)

    def ask_ai_chat(self):
        prompt = self.command_var.get().strip()
        if not prompt:
            prompt = "Plan a productive day for me."
        self.command_var.set("")
        self.append_chat("user", prompt)
        self.update_status("AI thinking...")

        def worker():
            try:
                response = self.assistant.ask_ai(prompt)
                spoken = self.assistant.speak(response)
                self.schedule_ui(self.append_chat, "assistant", response)
                if spoken:
                    self.schedule_ui(self.update_status, "AI ready")
                else:
                    self.schedule_ui(self.show_speech_error, self.assistant.last_speech_error)
                self.schedule_ui(self.update_dashboard)
            except Exception as exc:
                self.schedule_ui(self.append_chat, "assistant", f"AI error: {exc}")
                self.schedule_ui(self.update_status, "AI error")

        threading.Thread(target=worker, daemon=True).start()

    def daily_brief_chat(self):
        brief = self.assistant.daily_brief()
        self.append_chat("assistant", brief)

        def worker():
            if self.assistant.speak(brief):
                self.schedule_ui(self.update_status, "Daily brief spoken")
            else:
                self.schedule_ui(self.show_speech_error, self.assistant.last_speech_error)

        threading.Thread(target=worker, daemon=True).start()


def launch_gui(assistant):
    if tk is None:
        print("Tkinter is not available. Running in terminal mode.")
        assistant.run()
        return

    try:
        root = tk.Tk()
        app = YAMApp(root, assistant)
        root.mainloop()
    except Exception as exc:
        print(f"GUI launch failed: {exc}")
        assistant.run()


if __name__ == "__main__":
    print_banner()
    assistant = YAMAssistant()
    launch_gui(assistant)
