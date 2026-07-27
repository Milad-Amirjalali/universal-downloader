import sys
import io
import argparse
from pathlib import Path

# Ensure UTF-8 output encoding for Persian text in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from extractor import download_best_audio, format_quality_report, probe_audio_formats
from config import BOT_TOKEN



def run_cli_test(url: str):
    """
    Runs CLI mode to test YouTube link processing and inspect audio quality directly in terminal.
    """
    print("=" * 60)
    print("🚀 **شروع تست کیفیت و استخراج موزیک از یوتیوب (CLI Mode)**")
    print("=" * 60)
    print(f"🔗 **لینک ورود**: {url}\n")

    print("🔍 در حال آنالیز کیفیت‌های صوتی موجود در یوتیوب...")
    try:
        probe_data = probe_audio_formats(url)
        print(f"📌 عنوان: {probe_data.get('title')}")
        print(f"👤 کانال/خواننده: {probe_data.get('uploader')}")
        print(f"⏱ مدت زمان: {probe_data.get('duration')} ثانیه")
        best = probe_data.get('best_stream')
        if best:
            print(f"📡 بالاترین بیت‌ریت موجود یوتیوب: {best.get('abr')} kbps (کدک: {best.get('acodec')})\n")
    except Exception as e:
        print(f"⚠️ آنالیز پیش‌فرض خطا داشت ({e})، ادامه فرایند دانلود...")
        probe_data = None

    print("📥 در حال دانلود و استخراج با بالاترین کیفیت (320kbps MP3)...")
    result = download_best_audio(url)

    print("\n" + "=" * 60)
    print("📊 **نتایج آنالیز و گزارش تست کیفیت فایل استخراج شده:**")
    print("=" * 60)
    report = format_quality_report(result['quality_report'], probe_data)
    print(report)
    print("\n💾 **مسیر فایل ذخیره شده در سیستم**:")
    print(result['file_path'])
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="ربات استخراج موزیک با کیفیت عالی از یوتیوب")
    parser.add_argument("--cli", type=str, help="تست مستقیم یک لینک یوتیوب در محیط خط فرمان")
    parser.add_argument("--bot", action="store_true", help="اجرای ربات تلگرام")

    args = parser.parse_args()

    if args.cli:
        run_cli_test(args.cli)
    else:
        # Default to bot if no cli arg, or prompt if BOT_TOKEN missing
        if not BOT_TOKEN and not args.cli:
            print("⚠️ **توجه**: توکن ربات تلگرام (BOT_TOKEN) در فایل .env تعریف نشده است.")
            print("💡 می‌توانید برای تست مستقیم از دستور زیر در خط فرمان استفاده کنید:")
            print('   python main.py --cli "https://www.youtube.com/watch?v=..."\n')
            print("جهت اجرای ربات تلگرام، لطفاً توکن خود را در فایل .env قرار دهید.")
            return

        from bot import run_bot
        run_bot()


if __name__ == '__main__':
    main()
