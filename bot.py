import re
import os
import logging
from typing import Optional
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from extractor import download_best_audio, format_quality_report, probe_audio_formats

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/(watch\?v=|shorts/|[\w-]{11})[\S]*'


def is_youtube_url(text: str) -> bool:
    return bool(re.search(YOUTUBE_REGEX, text))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **سلام! به ربات استخراج موزیک با بالاترین کیفیت خوش آمدید.**\n\n"
        "🔗 کافیست **لینک ویدیو یا موزیک یوتیوب** (یوتیوب معمولی، Shorts یا YouTube Music) را برام ارسال کنی.\n\n"
        "✨ **ویژگی‌های ربات:**\n"
        "⚡️ استخراج با بالاترین کیفیت صوتی ممکن (320kbps MP3)\n"
        "📊 آنالیز و تست خودکار کیفیت فایل (Bitrate، Sample Rate، حجم)\n"
        "🎨 افزودن خودکار کاور اصلی ویدیو و متادیتا (عنوان و نام خواننده)\n"
        "📻 پخش مستقیم در موزیک پلیر تلگرام\n\n"
        "👇 همین الان یک لینک برام بفرست!"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_youtube_url(url):
        await update.message.reply_text("❌ لطفاً یک لینک معتبر از یوتیوب یا YouTube Music ارسال کنید.")
        return

    status_msg = await update.message.reply_text("🔍 **در حال بررسی لینک و آنالیز کیفیت‌های صوتی موجود...**", parse_mode='Markdown')

    try:
        # Step 1: Probe formats
        probe_data = probe_audio_formats(url)
        best_abr = probe_data.get('best_stream', {}).get('abr', 'نامشخص')
        
        await status_msg.edit_text(
            f"🎵 **ویدیو پیدا شد:** `{probe_data.get('title')}`\n"
            f"📡 **بهترین کیفیت صوتی یافت شده در یوتیوب**: `{best_abr} kbps`\n"
            "📥 **در حال استخراج و تبدیل به باکیفیت‌ترین فرمت MP3 (320kbps)...**",
            parse_mode='Markdown'
        )

        # Step 2: Download & Extract Audio with max quality
        result = download_best_audio(url)

        await status_msg.edit_text("⚙️ **در حال آنالیز فنی و سنجش کیفیت فایل استخراج شده...**", parse_mode='Markdown')

        audio_path = result['file_path']
        quality_data = result['quality_report']
        caption = format_quality_report(quality_data, probe_data)

        await status_msg.edit_text("📤 **در حال ارسال فایل صوتی به تلگرام...**", parse_mode='Markdown')

        # Step 3: Send audio file
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=result.get('title', 'Unknown Title'),
                performer=result.get('artist', 'YouTube'),
                duration=int(result.get('duration', 0)),
                caption=caption,
                parse_mode='Markdown'
            )

        await status_msg.delete()

        # Clean up temporary audio file after sending
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        logger.error(f"خطا در پردازش لینک {url}: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ **خطایی رخ داد**: {str(e)}", parse_mode='Markdown')


def run_bot(token: Optional[str] = None):
    bot_token = token or BOT_TOKEN
    if not bot_token:
        raise ValueError("توکن ربات تلگرام تنظیم نشده است! لطفاً فایل .env را مقداردهی کنید.")

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_youtube_link))

    print("🚀 ربات استخراج موزیک یوتیوب فعال شد...")
    app.run_polling()


if __name__ == '__main__':
    run_bot()
