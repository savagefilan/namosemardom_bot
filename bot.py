import telebot
from telebot import types

bot = telebot.TeleBot("8596969357:AAEWBl0wXCj5ORnc8Hv5CnkQKEn5UvSONKY")

# دیکشنری برای ذخیره file_id ویدیوها (می‌تونی بعداً با دیتابیس جایگزین کنی)
video_storage = {}  # مثلاً {user_id: {"video1": "file_id1", "video2": "file_id2"}}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! ویدیو بفرست تا ذخیره کنم. بعد با /videos لیستشون رو ببین.")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    user_id = message.from_user.id
    file_id = message.video.file_id
    file_name = message.video.file_name or f"video_{len(video_storage.get(user_id, {})) + 1}"
    
    if user_id not in video_storage:
        video_storage[user_id] = {}
    
    video_storage[user_id][file_name] = file_id
    bot.reply_to(message, f"✅ ویدیو با نام `{file_name}` ذخیره شد.\n\nبرای ارسال دوباره: `/send {file_name}`")

@bot.message_handler(commands=['videos'])
def list_videos(message):
    user_id = message.from_user.id
    videos = video_storage.get(user_id, {})
    
    if not videos:
        bot.reply_to(message, "هنوز هیچ ویدیویی ذخیره نکردی.")
        return
    
    text = "📽️ ویدیوهای ذخیره شده:\n\n"
    for name in videos.keys():
        text += f"/send_{name}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['send'])
def send_video_command(message):
    user_id = message.from_user.id
    try:
        # مثلاً /send video1
        video_name = message.text.split(maxsplit=1)[1]
        file_id = video_storage.get(user_id, {}).get(video_name)
        
        if file_id:
            bot.send_video(message.chat.id, file_id, caption=f"🎥 {video_name}")
        else:
            bot.reply_to(message, "این ویدیو پیدا نشد.")
    except:
        bot.reply_to(message, "دستور درست: `/send نام_ویدیو`")

# برای راحتی بیشتر می‌تونی این خط رو اضافه کنی:
@bot.message_handler(regexp=r'^/send_(.+)$')
def quick_send(message):
    user_id = message.from_user.id
    video_name = message.text[6:]  # بعد از /send_
    file_id = video_storage.get(user_id, {}).get(video_name)
    if file_id:
        bot.send_video(message.chat.id, file_id, caption=f"🎥 {video_name}")
    else:
        bot.reply_to(message, "ویدیو پیدا نشد.")

print("ربات در حال اجراست...")
bot.infinity_polling()