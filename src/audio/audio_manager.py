import os
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class AudioSettings:
    tts_enabled: bool = False
    sound_effects_enabled: bool = False
    tts_rate: int = 150
    tts_volume: int = 100
    tts_voice: Optional[str] = None
    music_enabled: bool = False
    ambient_sounds: bool = False


class TextToSpeech:
    def __init__(self):
        self.enabled: bool = False
        self.rate: int = 150
        self.volume: int = 100
        self.voice: Optional[str] = None
        self._detect_available_voices()

    def _detect_available_voices(self) -> None:
        system = platform.system()
        if system == "Windows":
            self._windows_available = True
        elif system == "Darwin":
            self._macos_available = True
        else:
            self._linux_available = True

    def speak(self, text: str, interrupt: bool = True) -> None:
        if not self.enabled:
            return

        if interrupt:
            self._stop_speaking()

        try:
            if platform.system() == "Windows":
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume / 100)
                if self.voice:
                    engine.setProperty('voice', self.voice)
                engine.say(text)
                engine.runAndWait()
            elif platform.system() == "Darwin":
                subprocess.run(['say', text], check=True)
            else:
                subprocess.run(['espeak', text], check=True)
        except Exception:
            self._fallback_speak(text)

    def _stop_speaking(self) -> None:
        pass

    def _fallback_speak(self, text: str) -> None:
        print(f"[TTS] {text}")

    def set_rate(self, rate: int) -> None:
        self.rate = max(50, min(300, rate))

    def set_volume(self, volume: int) -> None:
        self.volume = max(0, min(100, volume))

    def set_voice(self, voice_id: str) -> None:
        self.voice = voice_id

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def get_available_voices(self) -> list[str]:
        try:
            if platform.system() == "Windows":
                import pyttsx3
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                return [v.id for v in voices]
        except Exception:
            pass
        return ["default"]

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "rate": self.rate,
            "volume": self.volume,
            "voice": self.voice,
        }

    def load_from_dict(self, data: dict) -> None:
        self.enabled = data.get("enabled", False)
        self.rate = data.get("rate", 150)
        self.volume = data.get("volume", 100)
        self.voice = data.get("voice")


class SoundCue:
    def __init__(self, name: str, ascii_art: Optional[str] = None, beep_pattern: str = ""):
        self.name = name
        self.ascii_art = ascii_art
        self.beep_pattern = beep_pattern

    def play(self) -> None:
        if self.ascii_art:
            print(self.ascii_art)

        if self.beep_pattern:
            try:
                if platform.system() == "Windows":
                    import winsound
                    for char in self.beep_pattern:
                        if char == '.':
                            winsound.Beep(800, 100)
                        elif char == '-':
                            winsound.Beep(800, 300)
                        elif char == ' ':
                            import time
                            time.sleep(0.1)
                else:
                    import subprocess
                    subprocess.run(['printf', '\\a'], check=False)
            except Exception:
                pass


class SoundManager:
    SOUND_CUES = {
        "action": SoundCue(
            "action",
            ascii_art=None,
            beep_pattern="..."
        ),
        "success": SoundCue(
            "success",
            beep_pattern=".-."
        ),
        "failure": SoundCue(
            "failure",
            beep_pattern="---"
        ),
        "alert": SoundCue(
            "alert",
            beep_pattern="---."
        ),
        "comic": SoundCue(
            "comic",
            beep_pattern=".-..-."
        ),
        "menu": SoundCue(
            "menu",
            beep_pattern="."
        ),
        "coin": SoundCue(
            "coin",
            beep_pattern=".-.-."
        ),
        "police": SoundCue(
            "police",
            beep_pattern="..-..-..-"
        ),
    }

    def __init__(self):
        self.enabled: bool = False
        self.volume: int = 100
        self.muted_sounds: set[str] = set()

    def play(self, cue_name: str) -> None:
        if not self.enabled or cue_name in self.muted_sounds:
            return

        cue = self.SOUND_CUES.get(cue_name)
        if cue:
            cue.play()

    def action(self) -> None:
        self.play("action")

    def success(self) -> None:
        self.play("success")

    def failure(self) -> None:
        self.play("failure")

    def alert(self) -> None:
        self.play("alert")

    def police(self) -> None:
        self.play("police")

    def coin(self) -> None:
        self.play("coin")

    def menu_select(self) -> None:
        self.play("menu")

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def mute_sound(self, sound_name: str) -> None:
        self.muted_sounds.add(sound_name)

    def unmute_sound(self, sound_name: str) -> None:
        self.muted_sounds.discard(sound_name)

    def set_volume(self, volume: int) -> None:
        self.volume = max(0, min(100, volume))

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "volume": self.volume,
            "muted_sounds": list(self.muted_sounds),
        }

    def load_from_dict(self, data: dict) -> None:
        self.enabled = data.get("enabled", False)
        self.volume = data.get("volume", 100)
        self.muted_sounds = set(data.get("muted_sounds", []))


class AudioManager:
    def __init__(self):
        self.tts = TextToSpeech()
        self.sounds = SoundManager()
        self.settings = AudioSettings()
        self._load_preferences()

    def _load_preferences(self) -> None:
        try:
            import json
            prefs_file = "data/audio_prefs.json"
            if os.path.exists(prefs_file):
                with open(prefs_file, "r") as f:
                    prefs = json.load(f)
                self.tts.load_from_dict(prefs.get("tts", {}))
                self.sounds.load_from_dict(prefs.get("sounds", {}))
        except Exception:
            pass

    def save_preferences(self) -> None:
        try:
            import json
            os.makedirs("data", exist_ok=True)
            prefs_file = "data/audio_prefs.json"
            prefs = {
                "tts": self.tts.to_dict(),
                "sounds": self.sounds.to_dict(),
            }
            with open(prefs_file, "w") as f:
                json.dump(prefs, f, indent=2)
        except Exception:
            pass

    def speak_text(self, text: str) -> None:
        self.tts.speak(text)

    def play_sound(self, sound_name: str) -> None:
        self.sounds.play(sound_name)

    def enable_tts(self) -> None:
        self.tts.enable()
        self.settings.tts_enabled = True

    def disable_tts(self) -> None:
        self.tts.disable()
        self.settings.tts_enabled = False

    def enable_sounds(self) -> None:
        self.sounds.enable()
        self.settings.sound_effects_enabled = True

    def disable_sounds(self) -> None:
        self.sounds.disable()
        self.settings.sound_effects_enabled = False

    def toggle_tts(self) -> bool:
        return self.tts.toggle()

    def toggle_sounds(self) -> bool:
        return self.sounds.toggle()

    def is_tts_enabled(self) -> bool:
        return self.tts.enabled

    def is_sounds_enabled(self) -> bool:
        return self.sounds.enabled

    def to_dict(self) -> dict:
        return {
            "tts": self.tts.to_dict(),
            "sounds": self.sounds.to_dict(),
            "settings": {
                "tts_enabled": self.settings.tts_enabled,
                "sound_effects_enabled": self.settings.sound_effects_enabled,
            }
        }

    def load_from_dict(self, data: dict) -> None:
        if "tts" in data:
            self.tts.load_from_dict(data["tts"])
        if "sounds" in data:
            self.sounds.load_from_dict(data["sounds"])
        if "settings" in data:
            self.settings.tts_enabled = data["settings"].get("tts_enabled", False)
            self.settings.sound_effects_enabled = data["settings"].get("sound_effects_enabled", False)