import os
import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
WEB_DIR = BASE_DIR / "web"
VERSION_INFO = BASE_DIR / "file_version_info.txt"

from extractor import find_deno_executable


def clean_temp_files():
    """Cleans up temporary build directories and scratch files before compilation."""
    print("🧹 در حال پاک‌سازی فایل‌ها و پوشه‌های موقت...")
    build_dir = BASE_DIR / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    downloads_dir = BASE_DIR / "downloads"
    if downloads_dir.exists():
        for item in downloads_dir.glob("*"):
            if item.is_file():
                try:
                    item.unlink()
                except Exception:
                    pass


def build():
    clean_temp_files()

    deno_exe = find_deno_executable() or (BASE_DIR / "venv" / "Scripts" / "deno.exe")
    print(f"📌 استفاده از موتر Deno: {deno_exe}")

    print("🚀 در حال ساخت فایل اجرایی جدید ویندوز با متادیتای رسمی آنتی‌ویروس (.exe)...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "YouTube Music Pro",
        f"--version-file={VERSION_INFO}",
        f"--add-data={WEB_DIR}{os.pathsep}web",
        f"--add-binary={deno_exe}{os.pathsep}.",
        "--hidden-import", "yt_dlp",
        "--hidden-import", "mutagen",
        "--hidden-import", "webview",
        "--hidden-import", "auto_cookies",
        "--hidden-import", "yt_dlp_ejs",
        "gui_app.py"
    ]
    
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode == 0:
        exe_path = BASE_DIR / "dist" / "YouTube Music Pro.exe"
        print("\n" + "=" * 60)
        print("🎉 **ساخت فایل اجرایی رسمی ویندوز با موفقیت انجام شد!**")
        print(f"📁 **مسیر فایل .exe تولید شده**: {exe_path}")
        print("=" * 60)
    else:
        print("❌ خطا در فرآیند کامپایل و ساخت فایل .exe")


if __name__ == '__main__':
    build()
