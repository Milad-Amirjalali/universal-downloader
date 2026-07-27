import os
import sys
import glob
import shutil
import tempfile
import logging
from pathlib import Path
from http.cookiejar import MozillaCookieJar
import browser_cookie3
from yt_dlp.cookies import extract_cookies_from_browser

logger = logging.getLogger(__name__)


def copy_file_safe(src: str, dst: str) -> bool:
    """Safely copies a file even if locked by an active browser process."""
    try:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            return True
    except Exception as e:
        logger.debug(f"Copy error for {src}: {e}")
    return False


def auto_generate_cookies(cookies_path: Path) -> bool:
    """
    Automatically extracts YouTube & Google cookies from installed browsers
    (Firefox, Chrome, Edge, Brave, Opera) and saves to cookies.txt.
    Supports bypass for locked browser database files on Windows.
    """
    try:
        jar = MozillaCookieJar(str(cookies_path))
        extracted_count = 0

        # 1. Try yt-dlp / browser_cookie3 direct extraction for Firefox, Chrome, Edge, Brave, Opera
        for browser in ['firefox', 'edge', 'chrome', 'brave', 'opera']:
            try:
                cj = extract_cookies_from_browser(browser)
                if cj:
                    for cookie in cj:
                        if any(domain in cookie.domain for domain in ['youtube.com', 'google.com', 'youtu.be']):
                            jar.set_cookie(cookie)
                            extracted_count += 1
                    if extracted_count > 0:
                        jar.save(ignore_discard=True, ignore_expires=True)
                        logger.info(f"Extracted {extracted_count} cookies from {browser}")
                        return True
            except Exception as e:
                logger.debug(f"Direct extraction failed for {browser}: {e}")
                continue

        # 2. Fallback: Copy locked SQLite cookies files from Chrome / Edge / Brave AppData to temp
        appdata_local = os.getenv('LOCALAPPDATA', '')
        appdata_roaming = os.getenv('APPDATA', '')
        temp_dir = tempfile.gettempdir()

        browser_paths = [
            # Chrome
            ('chrome', os.path.join(appdata_local, r'Google\Chrome\User Data\Default\Network\Cookies')),
            # Edge
            ('edge', os.path.join(appdata_local, r'Microsoft\Edge\User Data\Default\Network\Cookies')),
            # Brave
            ('brave', os.path.join(appdata_local, r'BraveSoftware\Brave-Browser\User Data\Default\Network\Cookies')),
            # Opera
            ('opera', os.path.join(appdata_roaming, r'Opera Software\Opera Stable\Network\Cookies')),
        ]

        for browser_name, cookie_file in browser_paths:
            if os.path.exists(cookie_file):
                temp_cookie_file = os.path.join(temp_dir, f"{browser_name}_temp_cookies.sqlite")
                if copy_file_safe(cookie_file, temp_cookie_file):
                    try:
                        # Extract from temporary copy using browser_cookie3
                        if browser_name == 'chrome':
                            cj = browser_cookie3.chrome(cookie_file=temp_cookie_file)
                        elif browser_name == 'edge':
                            cj = browser_cookie3.edge(cookie_file=temp_cookie_file)
                        elif browser_name == 'brave':
                            cj = browser_cookie3.brave(cookie_file=temp_cookie_file)
                        elif browser_name == 'opera':
                            cj = browser_cookie3.opera(cookie_file=temp_cookie_file)
                        else:
                            cj = None

                        if cj:
                            for cookie in cj:
                                if any(d in cookie.domain for d in ['youtube.com', 'google.com', 'youtu.be']):
                                    jar.set_cookie(cookie)
                                    extracted_count += 1
                            if extracted_count > 0:
                                jar.save(ignore_discard=True, ignore_expires=True)
                                logger.info(f"Extracted {extracted_count} cookies via temp copy from {browser_name}")
                                return True
                    except Exception as err:
                        logger.debug(f"Temp copy cookie parse error ({browser_name}): {err}")

        return extracted_count > 0
    except Exception as e:
        logger.warning(f"Auto cookie generation error: {e}")
        return False
