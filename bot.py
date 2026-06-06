import telebot
import json
import os
import time
import threading
from telebot import types

TOKEN = os.getenv("TOKEN") or "8596969357:AAEWBl0wXCj5ORnc8Hv5CnkQKEn5UvSONKY"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6649749290
BOT_USERNAME = "namosemardom_bot"
FILE_NAME = "videos.json"

CHANNEL_1_ID = -1002168285432
CHANNEL_2_ID = -1003517185269

CHANNEL_1_LINK = "https://t.me/+fqQdF2eL3xJiODlk"
CHANNEL_2_LINK = "https://t.me/+0GccRvh-sRpmNDlk"

# بارگذاری ویدیوها
if os.path.exists(FILE_NAME):
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            videos = json.load(f)
    except:
        videos = []
else:
    videos = []

def save_videos():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(videos, f)

def is_member_in_both_channels(user_id):
    try:
        m1 = bot.get_chat_member(CHANNEL_1_ID, user_id).status
        m2 = bot.get_chat_member(CHANNEL_2_ID, user_id).status
        print(f"User {user_id} -> Ch1: {m1} | Ch2: {m2}")  # لاگ مهم
        return m1 in ["member", "administrator", "creator"] and m2 in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"خطا در چک عضویت: {e}")
        return False

def show_join_message(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("👉 کانال اول", url=CHANNEL_1_LINK))
    markup.add(types.InlineKeyboardButton("👉 کانال دوم", url=CHANNEL_2_LINK))
    markup.add(types.InlineKeyboardButton("✅ عضو شدم 👌", callback_data="check_membership"))
    
    bot.reply_to(message, "😈 باید عضو بشی اول خوشگله !\n\n"
                         "عضو هر دو کانال شو و بعد روی دکمه «عضو شدم 👌» بزن.", 
                 reply_markup=markup)

def delete_message_after(chat_id, message_id, delay=30):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    text = message.text.split()

    # Deep Link (لینک ویدیو)
    if len(text) > 1:
        try:
            num = int(text[1])
            if 1 <= num <= len(videos):
                if user_id != ADMIN_ID and not is_member_in_both_channels(user_id):
                    show_join_message(message)
                    return
                caption = "سفارشت حاضره شیطون 😈\nاین پیام بعد از ۳۰ ثانیه پاک میشه !! 🫶🏻"
                sent = bot.send_video(message.chat.id, videos[num-1], caption=caption)
                threading.Thread(target=delete_message_after, args=(message.chat.id, sent.message_id, 30), daemon=True).start()
                return
        except:
            pass

    if user_id == ADMIN_ID:
        bot.reply_to(message, f"✅ خوش اومدی ادمین!\nتعداد ویدیوها: {len(videos)}")
        return

    # کاربر معمولی
    if not is_member_in_both_channels(user_id):
        show_join_message(message)
        return

    bot.reply_to(message, "✅ عضویتت تأیید شد!\nحالا می‌تونی ویدیو ببینی.")

@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    if is_member_in_both_channels(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ تبریک!")
        bot.edit_message_text("🎉 عضوی از ما شدی خوشگله !!\n\n/start بزن", 
                             call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو هر دو کانال نشدی!", show_alert=True)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ فقط ادمین اجازه آپلود داره.")
        return
    videos.append(message.video.file_id)
    save_videos()
    number = len(videos)
    link = f"https://t.me/{BOT_USERNAME}?start={number}"
    bot.reply_to(message, f"✅ **ویدیو شماره {number}** ذخیره شد!\n\n`{link}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def all_messages(message):
    if message.from_user.id != ADMIN_ID:
        show_join_message(message)

print("✅ ربات با عضویت اجباری فعال شد!")
bot.infinity_polling()
