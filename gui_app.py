import os
import sys
import base64
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import webview

# Ensure UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from extractor import probe_audio_formats, download_media
from config import USER_MUSIC_DIR, USER_VIDEO_DIR

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)


class DesktopApi:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def open_music_folder(self):
        """Opens current Windows user's Music download directory in Explorer."""
        try:
            folder_path = str(USER_MUSIC_DIR.resolve())
            os.startfile(folder_path)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error opening music folder: {e}")
            return {"success": False, "error": str(e)}

    def open_video_folder(self):
        """Opens current Windows user's Videos download directory in Explorer."""
        try:
            folder_path = str(USER_VIDEO_DIR.resolve())
            os.startfile(folder_path)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error opening video folder: {e}")
            return {"success": False, "error": str(e)}

    def probe_url(self, url: str):
        """Probes media metadata asynchronously in background thread."""
        future = executor.submit(self._probe_url_task, url)
        return future.result(timeout=20)

    def _probe_url_task(self, url: str):
        try:
            data = probe_audio_formats(url)
            return {
                "success": True,
                "title": data.get('title'),
                "uploader": data.get('uploader'),
                "duration": data.get('duration', 0),
                "thumbnail": data.get('thumbnail'),
                "best_resolution": data.get('best_resolution', '1080p'),
                "best_abr": data.get('best_abr', '320 kbps'),
            }
        except Exception as e:
            logger.error(f"Probe error: {e}")
            return {"success": False, "error": str(e)}

    def download_media(self, url: str, mode: str = "audio"):
        """Downloads audio ('audio'), video ('video'), or both ('both') asynchronously."""
        future = executor.submit(self._download_media_task, url, mode)
        return future.result(timeout=400)

    def _download_media_task(self, url: str, mode: str):
        try:
            result = download_media(url, mode)
            file_path = result.get('file_path')

            audio_data_uri = ""
            if file_path and file_path.endswith('.mp3') and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                audio_data_uri = f"data:audio/mp3;base64,{encoded}"

            return {
                "success": True,
                "type": result.get('type'),
                "file_path": file_path,
                "audio_url": audio_data_uri,
                "title": result.get('title'),
                "quality": result.get('quality_report'),
                "music_folder": str(USER_MUSIC_DIR),
                "video_folder": str(USER_VIDEO_DIR),
            }
        except Exception as e:
            logger.error(f"Download error: {e}")
            return {"success": False, "error": str(e)}


def main():
    api = DesktopApi()
    html_path = Path(__file__).parent / "web" / "index.html"
    
    window = webview.create_window(
        title="Universal Media Downloader Pro - دانلود ویدیو و موزیک با کیفیت عالی",
        url=str(html_path.resolve()),
        js_api=api,
        width=960,
        height=800,
        resizable=True,
        min_size=(840, 640),
        background_color="#0B0E14"
    )
    api.set_window(window)
    webview.start(debug=False)


if __name__ == '__main__':
    main()
