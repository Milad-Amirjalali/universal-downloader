import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Dynamic user paths based on logged-in Windows user profile
USER_HOME = Path.home()
USER_MUSIC_DIR = USER_HOME / "Downloads" / "Music"
USER_VIDEO_DIR = USER_HOME / "Downloads" / "Videos"

# Create directories automatically if they do not exist
USER_MUSIC_DIR.mkdir(parents=True, exist_ok=True)
USER_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Default audio/video quality settings
DEFAULT_AUDIO_FORMAT = "mp3"
DEFAULT_AUDIO_QUALITY = "320"  # 320 kbps MP3
DEFAULT_VIDEO_FORMAT = "mp4"
