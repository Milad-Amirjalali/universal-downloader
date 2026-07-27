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
ISS_PATH = BASE_DIR / "setup_installer.iss"
RELEASES_DIR = BASE_DIR / "releases"


def find_iscc() -> str:
    """Finds ISCC.exe from PATH, Program Files, or AppData Local Programs."""
    iscc_path = shutil.which("iscc")
    if iscc_path:
        return iscc_path

    possible_paths = [
        Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
    ]

    for p in possible_paths:
        if p.exists():
            return str(p)

    raise FileNotFoundError("فایل کامپایلر Inno Setup (ISCC.exe) پیدا نشد.")


def build_setup_installer():
    print("🚀 در حال ساخت فایل نصب‌کننده استاندارد ویندوز (Setup.exe)...")
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    iscc_bin = find_iscc()
    print(f"📌 استفاده از کامپایلر Inno Setup: {iscc_bin}")

    cmd = [iscc_bin, str(ISS_PATH)]
    result = subprocess.run(cmd, cwd=BASE_DIR)

    if result.returncode == 0:
        setup_exe = RELEASES_DIR / "Setup_YouTube_Media_Downloader_v1.0.exe"
        print("\n" + "=" * 60)
        print("🎉 **فایل نصب‌کننده ویندوز با موفقیت ساخته شد!**")
        print(f"📦 **مسیر فایل نصب‌کننده (Setup.exe)**: {setup_exe}")
        print("=" * 60)
    else:
        print("❌ خطا در فرآیند کامپایل فایل نصب‌کننده.")


if __name__ == '__main__':
    build_setup_installer()
