import telebot
import random
import time
from telebot import types
import threading

token = "8127189495:AAGCTxXXsoyH-EHSJJvQ07uYHCrz4Ez7hqc"
bot = telebot.TeleBot(token)

userstates = {}
setting_limits = {}
channels_where_admin = []
tokens = {}
userchannels = {}
limits = {}
waiting_users = {}
current_tokens = {}
complainted = []
blacklist = []


def give_token():
    english_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                       'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                       'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['#', '$', '&']

    allchars = english_letters + digits + symbols
    result = ""

    for i in range(10):
        result += random.choice(allchars)

    while result in tokens.values():
        result = ""
        for i in range(10):
            result += random.choice(allchars)

    return result


def check_is_admin(user_id, chat_admins):
    for admin in chat_admins:
        if user_id == admin.user.id:
            return True
    return False


def get_chan_id(user_id):
    if user_id not in current_tokens:
        return False
    for i in tokens.keys():
        if tokens[i] == current_tokens[user_id]:
            if i in channels_where_admin:
                return i
    return False


def is_in_ban(message):
    username = message.from_user.id
    if username in blacklist:
        bot.send_message(message.chat.id,
                         "🚫 *К сожалению, доступ к боту для вас ограничен*\n\n"
                         "Если вы считаете, что это ошибка, свяжитесь с поддержкой.",
                         parse_mode='Markdown')
        return False
    return True


def send_anonymous_media(channel_id, original_message):
    """Отправляет медиа-сообщения анонимно с кастомным текстом"""
    try:
        header = "📨 *Анонимное сообщение:*\n\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⚠️ Пожаловаться", callback_data=f"complaint_{original_message.message_id}"))

        if original_message.content_type == 'photo':
            new_caption = f"{header}{original_message.caption or ''}"
            bot.send_photo(channel_id, original_message.photo[-1].file_id,
                           caption=new_caption, parse_mode='Markdown', reply_markup=markup)

        elif original_message.content_type == 'video':
            new_caption = f"{header}{original_message.caption or ''}"
            bot.send_video(channel_id, original_message.video.file_id,
                           caption=new_caption, parse_mode='Markdown', reply_markup=markup)

        elif original_message.content_type == 'audio':
            new_caption = f"{header}{original_message.caption or ''}"
            bot.send_audio(channel_id, original_message.audio.file_id,
                           caption=new_caption, parse_mode='Markdown', reply_markup=markup)

        elif original_message.content_type == 'document':
            new_caption = f"{header}{original_message.caption or ''}"
            bot.send_document(channel_id, original_message.document.file_id,
                              caption=new_caption, parse_mode='Markdown', reply_markup=markup)

        elif original_message.content_type == 'voice':
            bot.send_voice(channel_id, original_message.voice.file_id)

        elif original_message.content_type == 'video_note':
            bot.send_video_note(channel_id, original_message.video_note.file_id)

        elif original_message.content_type == 'sticker':
            bot.send_sticker(channel_id, original_message.sticker.file_id)

        return True
    except Exception as e:
        print(f"Ошибка отправки медиа: {e}")
        return False


@bot.message_handler(commands=['start'])
def start(message):
    if not is_in_ban(message):
        return

    welcome_text = """
👋 *Добро пожаловать в Анонимный Бот!*

🤫 *Отправляйте сообщения в каналы полностью анонимно!*

✨ *Как это работает:*
1️⃣ 📨 Получите токен от администратора канала
2️⃣ 🔐 Отправьте сообщение через бота
3️⃣ 📢 Сообщение появится в канале полностью анонимно

🛠 *Доступные команды:*
/sendmessage - 📝 Написать анонимное сообщение
/register - 🔑 Подключить ваш канал (для администраторов)
/setlimit - ⚙️ Настроить лимиты для вашего канала
/donate - 💖 Поддержать разработку

👑 *Для администраторов каналов:*
Используйте /register чтобы подключить канал к боту и подтвердить свои права администратора.

🔒 *Гарантия анонимности:* 
Ваши сообщения полностью анонимны - даже мы не знаем кто их автор!

❗️ *Важно!*
После обновлений бота обновляется и список токенов, каналов и настроек!
    """

    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')
    user_id = message.from_user.id
    if user_id not in userstates:
        userstates[user_id] = {}
    userstates[user_id][message.chat.id] = 1


@bot.message_handler(commands=['donate'])
def donate(message):
    donate_text = """
💖 *Поддержать разработку*

Ваша поддержка помогает развивать бота и добавлять новые функции!

🌟 *Преимущества для доноров:*
• 🚀 Приоритетная поддержка
• 🔧 Ранний доступ к новым функциям
• 💎 Специальные возможности

💳 *Для донатов:*
В разработке...

Спасибо за вашу поддержку! 🙏
    """
    bot.send_message(message.chat.id, donate_text, parse_mode='Markdown')


@bot.message_handler(commands=['sendmessage'])
def sending(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in userstates:
        userstates[user_id] = {}

    if user_id not in current_tokens:
        bot.send_message(chat_id,
                         "📨 *Отправка анонимного сообщения*\n\n"
                         "🔑 Пожалуйста, пришлите токен канала, который вы получили от администратора...",
                         parse_mode='Markdown')
        userstates[user_id][chat_id] = 4
    else:
        chan_id = get_chan_id(user_id)
        if chan_id:
            if user_id not in waiting_users[chan_id]:
                userstates[user_id][chat_id] = 5
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
                bot.send_message(chat_id,
                                 f"✍️ *Готово к отправке!*\n\n"
                                 f"📢 Канал: `{bot.get_chat(chan_id).title}`\n\n"
                                 f"Напишите ваше сообщение для отправки:\n\n"
                                 f"💡 Можно отправлять: текст, фото, видео, стикеры, видео-сообщения и документы (если разрешено настройками канала)\n\n"
                                 f"🔐 Токен: `{current_tokens[user_id]}`",
                                 parse_mode='Markdown', reply_markup=markup)
            else:
                userstates[user_id][chat_id] = 1
                bot.send_message(chat_id,
                                 f"⏳ *Пожалуйста, подождите {limits[chan_id]['onemessper']} секунд*\n\n"
                                 f"Канал: {bot.get_chat(chan_id).title}\n\n"
                                 f"Это необходимо для предотвращения спама.",
                                 parse_mode='Markdown')
        else:
            userstates[user_id][chat_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Сменить токен", callback_data="wrongtok_-1"))
            bot.send_message(chat_id,
                             "❌ *Токен недействителен!*\n\n"
                             "Возможно, токен был изменён или удалён администратором канала.\n"
                             "Пожалуйста, получите актуальный токен.",
                             parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(commands=['appendtoblacklist'])
def appendix(message):
    if message.from_user.id != 6720238906:
        return False
    username = message.text.split(" ")[1]
    if username not in blacklist:
        blacklist.append(username)
    bot.send_message(message.chat.id, "✅ Пользователь добавлен в черный список")


@bot.message_handler(commands=['removefromblacklist'])
def removix(message):
    if message.from_user.id != 6720238906:
        return False
    username = message.text.split(" ")[1]
    if username in blacklist:
        blacklist.remove(username)
    bot.send_message(message.chat.id, "✅ Пользователь удален из черного списка")


@bot.message_handler(commands=['register'])
def registering(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in userstates:
        userstates[user_id] = {}

    bot.send_message(chat_id,
                     "👑 *Подключение вашего канала*\n\n"
                     "📎 Пожалуйста, пришлите ссылку на ваш канал в формате:\n"
                     "• @username\n"
                     "• https://t.me/username\n\n"
                     "⚠️ *Предварительно убедитесь, что:*\n"
                     "• Бот добавлен в канал как администратор\n"
                     "• У бота есть права на отправку сообщений",
                     parse_mode='Markdown')
    userstates[user_id][chat_id] = 2


@bot.message_handler(commands=['setlimit'])
def limitsettings(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in userstates:
        userstates[user_id] = {}

    userstates[user_id][chat_id] = 6

    if user_id not in userchannels:
        bot.send_message(chat_id,
                         "😔 *У вас нет подключенных каналов!*\n\n"
                         "Для начала используйте команду /register чтобы подключить канал",
                         parse_mode='Markdown')
    else:
        chans = userchannels[user_id]
        available_chans = [chan for chan in chans if chan in channels_where_admin]

        if not available_chans:
            bot.send_message(chat_id,
                             "😔 *Нет доступных каналов для настройки!*\n\n"
                             "Добавьте бота как администратора в ваши каналы\n"
                             "или проверьте права доступа",
                             parse_mode='Markdown')
        else:
            userstates[user_id][chat_id] = 6
            markup = types.InlineKeyboardMarkup()
            for chan in available_chans:
                markup.add(types.InlineKeyboardButton(
                    f"📢 {bot.get_chat(chan).title}",
                    callback_data=f"setlimit_{chan}"
                ))
            bot.send_message(chat_id,
                             "⚙️ *Настройка лимитов для канала*\n\n"
                             "Выберите канал, для которого хотите изменить настройки:",
                             reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(content_types=['photo', "video", "audio", "sticker", "video_note", "document"])
def nottext(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in userstates:
        return

    if chat_id not in userstates[user_id]:
        return

    if userstates[user_id][chat_id] == 5:
        channel_id = get_chan_id(user_id)
        if not channel_id:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Токен стал недействительным!*\n\n"
                             "Токен был удалён администратором во время подготовки вашего сообщения.\n"
                             "Пожалуйста, получите новый токен.",
                             parse_mode='Markdown')
            return

        if not limits[channel_id]["cansendporn"]:
            bot.send_message(chat_id,
                             "🚫 *Отправка медиа-файлов запрещена!*\n\n"
                             "Администратор канала отключил возможность отправки медиа-файлов.\n"
                             "Вы можете отправить только текстовое сообщение.",
                             parse_mode='Markdown')
            return

        success = send_anonymous_media(channel_id, message)

        if success:
            userstates[user_id][chat_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📨 Отправить ещё сообщение", callback_data="resend_-1"))
            bot.send_message(chat_id,
                             "✅ *Ваше медиа-сообщение успешно отправлено!*\n\n"
                             "Сообщение доставлено в канал полностью анонимно 🎭",
                             parse_mode='Markdown', reply_markup=markup)

            waiting_users[channel_id].append(user_id)

            def background_task():
                time.sleep(limits[channel_id]["onemessper"])
                if channel_id in waiting_users and user_id in waiting_users[channel_id]:
                    waiting_users[channel_id].remove(user_id)

            threading.Thread(target=background_task).start()

            bot.send_message(6720238906,
                             f"📊 Медиа отправлено\n"
                             f"Тип: {message.content_type}\n"
                             f"От: {message.from_user.first_name}\n"
                             f"В канал: {channel_id}")


@bot.message_handler()
def main(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id not in userstates:
        userstates[user_id] = {}

    if chat_id not in userstates[user_id]:
        userstates[user_id][chat_id] = 1

    if userstates[user_id][chat_id] == 2:
        link = message.text
        if 't.me/' in link:
            username = link.split('t.me/')[-1].replace('@', '').split('/')[0]
        elif link.startswith('@'):
            username = link[1:]
        else:
            username = link

        try:
            chat_info = bot.get_chat(f"@{username}").id
            admins = bot.get_chat_administrators(chat_info)

            if check_is_admin(bot.get_me().id, admins):
                if chat_info not in channels_where_admin:
                    channels_where_admin.append(chat_info)

                if not check_is_admin(user_id, admins):
                    bot.send_message(chat_id,
                                     "❌ *Недостаточно прав!*\n\n"
                                     "Вы не являетесь администратором этого канала.\n"
                                     "Пожалуйста, убедитесь, что у вас есть права администратора.",
                                     parse_mode='Markdown')
                else:
                    if user_id not in userchannels:
                        userchannels[user_id] = []
                    userchannels[user_id].append(chat_info)
                    userstates[user_id][chat_id] = 3

                    if chat_info not in tokens:
                        tokens[chat_info] = give_token()
                    if chat_info not in waiting_users:
                        waiting_users[chat_info] = []
                    if chat_info not in limits:
                        limits[chat_info] = {"onemessper": 10, "cansendporn": True}

                    bot.send_message(chat_id,
                                     f"✅ *Канал успешно подключен!*\n\n"
                                     f"📢 Канал: {bot.get_chat(chat_info).title}\n\n"
                                     f"🔑 *Токен вашего канала:*\n"
                                     f"`{tokens[chat_info]}`\n\n"
                                     f"💡 *Сохраните этот токен в надежном месте!*\n"
                                     f"Выдавайте его только тем, кому хотите разрешить анонимную отправку сообщений.",
                                     parse_mode='Markdown')
            else:
                bot.send_message(chat_id,
                                 "👑 *Требуется действие!*\n\n"
                                 f"Пожалуйста, добавьте @{bot.get_me().username} как администратора в ваш канал\n\n"
                                 f"💡 *Необходимые права:*\n"
                                 f"• Отправка сообщений\n"
                                 f"• Редактирование сообщений",
                                 parse_mode='Markdown')

        except Exception as e:
            error_msg = str(e)
            if "chat not found" in error_msg:
                bot.send_message(chat_id,
                                 "❌ *Канал не найден!*\n\n"
                                 "Пожалуйста, проверьте правильность ссылки и убедитесь, что канал существует.",
                                 parse_mode='Markdown')
            elif "403" in error_msg:
                bot.send_message(chat_id,
                                 "🚫 *Бот заблокирован в канале!*\n\n"
                                 "Пожалуйста, разблокируйте бота в настройках канала.",
                                 parse_mode='Markdown')
            elif "inaccessible" in error_msg:
                bot.send_message(chat_id,
                                 "👑 *Недостаточно прав!*\n\n"
                                 "Добавьте бота как администратора с необходимыми правами.",
                                 parse_mode='Markdown')
            else:
                bot.send_message(chat_id,
                                 "❌ *Произошла ошибка!*\n\n"
                                 "Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой.",
                                 parse_mode='Markdown')

    elif userstates[user_id][chat_id] == 4:
        current_tokens[user_id] = message.text
        chan_id = get_chan_id(user_id)
        if chan_id:
            userstates[user_id][chat_id] = 5
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
            bot.send_message(chat_id,
                             f"✅ *Токен принят!*\n\n"
                             f"📢 Канал: `{bot.get_chat(chan_id).title}`\n\n"
                             f"✍️ Теперь напишите сообщение, которое хотите отправить анонимно:\n\n"
                             f"💡 Вы можете отправлять текст или медиа-файлы (если разрешено настройками канала)",
                             parse_mode='Markdown', reply_markup=markup)
        else:
            userstates[user_id][chat_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Попробовать другой токен", callback_data="wrongtok_-1"))
            bot.send_message(chat_id,
                             "❌ *Неверный токен!*\n\n"
                             "Возможно, токен был изменён администратором или срок его действия истёк.\n"
                             "Пожалуйста, получите актуальный токен у администратора канала.",
                             parse_mode='Markdown', reply_markup=markup)

    elif userstates[user_id][chat_id] == 5:
        channel_id = get_chan_id(user_id)

        if not channel_id:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Токен стал недействительным!*\n\n"
                             "Токен был удалён администратором во время отправки вашего сообщения.\n"
                             "Пожалуйста, получите новый токен.",
                             parse_mode='Markdown')
            return

        if len(message.text) >= 1500:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Слишком длинное сообщение!*\n\n"
                             "Максимальная длина сообщения - 1500 символов.\n"
                             "Пожалуйста, сократите ваше сообщение.",
                             parse_mode='Markdown')
            return

        userstates[user_id][chat_id] = 1

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📨 Отправить ещё сообщение", callback_data="resend_-1"))
        bot.send_message(chat_id,
                         "✅ *Сообщение успешно отправлено!*\n\n"
                         "Ваше сообщение доставлено в канал полностью анонимно 🎭\n"
                         "Никто не узнает, что это были именно вы!",
                         parse_mode='Markdown', reply_markup=markup)

        complaint_markup = types.InlineKeyboardMarkup()
        complaint_markup.add(
            types.InlineKeyboardButton("⚠️ Пожаловаться", callback_data=f"complaint_{message.message_id}"))

        bot.send_message(channel_id,
                         f"📨 *Анонимное сообщение:*\n\n{message.text}",
                         reply_markup=complaint_markup,
                         parse_mode='Markdown')

        waiting_users[channel_id].append(user_id)

        def background_task():
            time.sleep(limits[channel_id]["onemessper"])
            if channel_id in waiting_users and user_id in waiting_users[channel_id]:
                waiting_users[channel_id].remove(user_id)

        threading.Thread(target=background_task).start()

        bot.send_message(6720238906,
                         f"📊 Сообщение отправлено\n"
                         f"Текст: {message.text}\n"
                         f"От: {message.from_user.first_name}\n"
                         f"В канал: {channel_id}")

    elif userstates[user_id][chat_id] == 7:
        if user_id not in setting_limits:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Сессия настройки устарела!*\n\n"
                             "Пожалуйста, начните настройку заново.",
                             parse_mode='Markdown')
            return

        channel_id = setting_limits[user_id]
        if channel_id not in limits:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Канал больше не подключен!*",
                             parse_mode='Markdown')
            return

        mess_split = message.text.strip().split(" ")
        if len(mess_split) != 2:
            bot.send_message(chat_id,
                             "❌ *Неверный формат ввода!*\n\n"
                             "Пожалуйста, введите данные в формате: [время] [+/-]\n\n"
                             "📝 *Примеры:*\n"
                             "`60 +` - лимит 60 сек, медиа включено\n"
                             "`30 -` - лимит 30 сек, медиа выключено\n"
                             "`-1 +` - время не меняется, медиа включается\n\n"
                             "💡 *Примечание:*\n"
                             "Время от 10 до 180 секунд\n"
                             "+ включить медиа, - выключить медиа",
                             parse_mode='Markdown')
            return

        try:
            time_limit = int(mess_split[0])
            media_setting = mess_split[1]

            if (time_limit != -1 and (time_limit < 10 or time_limit > 180)):
                bot.send_message(chat_id,
                                 "❌ *Неверное значение времени!*\n\n"
                                 "Время должно быть от 10 до 180 секунд.\n"
                                 "Или используйте -1 чтобы не изменять текущее значение.",
                                 parse_mode='Markdown')
                return

            if media_setting not in ['+', '-', '-1']:
                bot.send_message(chat_id,
                                 "❌ *Неверная настройка медиа!*\n\n"
                                 "Используйте: + (включить) или - (выключить)\n"
                                 "Или -1 чтобы не изменять текущую настройку.",
                                 parse_mode='Markdown')
                return

            if time_limit != -1:
                limits[channel_id]["onemessper"] = time_limit
            if media_setting != '-1':
                limits[channel_id]["cansendporn"] = (media_setting == '+')

            userstates[user_id][chat_id] = 1
            media_status = "✅ Включена" if limits[channel_id]["cansendporn"] else "❌ Выключена"
            bot.send_message(chat_id,
                             f"✅ *Настройки успешно обновлены!*\n\n"
                             f"📢 Канал: {bot.get_chat(channel_id).title}\n\n"
                             f"⚙️ *Текущие настройки:*\n"
                             f"• ⏰ Интервал между сообщениями: {limits[channel_id]['onemessper']} сек\n"
                             f"• 📎 Отправка медиа-файлов: {media_status}",
                             parse_mode='Markdown')
            del setting_limits[user_id]

        except:
            bot.send_message(chat_id,
                             "❌ *Ошибка обработки данных!*\n\n"
                             "Пожалуйста, проверьте правильность введенных данных и попробуйте еще раз.",
                             parse_mode='Markdown')


@bot.my_chat_member_handler()
def handle_chat_member_update(message):
    new_status = message.new_chat_member.status

    if new_status == "administrator" and message.chat.id not in channels_where_admin:
        time.sleep(1)
        admins = bot.get_chat_administrators(message.chat.id)

        channels_where_admin.append(message.chat.id)
        waiting_users[message.chat.id] = []
        limits[message.chat.id] = {"onemessper": 10, "cansendporn": True}
        result = give_token()
        tokens[message.chat.id] = result

        for admin in admins:
            if admin.user.id not in userchannels:
                userchannels[admin.user.id] = []
            userchannels[admin.user.id].append(message.chat.id)

            if admin.user.id in userstates:
                for chat_id in userstates[admin.user.id]:
                    bot.send_message(admin.user.id,
                                     f"🎉 *Бот успешно добавлен как администратор!*\n\n"
                                     f"📢 Канал: {message.chat.title}\n\n"
                                     f"🔑 *Токен вашего канала:*\n"
                                     f"`{result}`\n\n"
                                     f"💡 *Сохраните этот токен!*\n"
                                     f"Выдавайте его пользователям для анонимной отправки сообщений.",
                                     parse_mode='Markdown')

    elif new_status in ["left", "kicked", "member"]:
        if message.chat.id in channels_where_admin:
            channels_where_admin.remove(message.chat.id)
        if message.chat.id in tokens:
            del tokens[message.chat.id]
        if message.chat.id in waiting_users:
            del waiting_users[message.chat.id]
        if message.chat.id in limits:
            del limits[message.chat.id]


@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if not is_in_ban(call.message):
        return

    destiny = call.data.split("_")[0]
    btn = int(call.data.split("_")[1])

    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id not in userstates:
        userstates[user_id] = {}

    if chat_id not in userstates[user_id]:
        userstates[user_id][chat_id] = 1

    if destiny == "setlimit":
        if btn not in channels_where_admin:
            userstates[user_id][chat_id] = 1
            bot.send_message(chat_id,
                             "❌ *Бот не является администратором!*\n\n"
                             "Пожалуйста, добавьте бота как администратора в этот канал.",
                             parse_mode='Markdown')
            return

        current = limits[btn]
        media_status = "✅ Включена" if current["cansendporn"] else "❌ Выключена"

        bot.send_message(chat_id,
                         f"⚙️ *Настройка лимитов для канала*\n\n"
                         f"📢 Канал: {bot.get_chat(btn).title}\n\n"
                         f"📊 *Текущие настройки:*\n"
                         f"• ⏰ Интервал между сообщениями: {current['onemessper']} сек\n"
                         f"• 📎 Отправка медиа-файлов: {media_status}\n\n"
                         f"✏️ *Введите новые настройки:*\n"
                         f"Формат: [время] [+/-]\n\n"
                         f"📝 *Примеры:*\n"
                         f"`60 +` - лимит 60 сек, медиа включено\n"
                         f"`30 -` - лимит 30 сек, медиа выключено\n"
                         f"`-1 +` - время не меняется, медиа включается\n\n"
                         f"💡 *Примечание:*\n"
                         f"• Время: от 10 до 180 секунд (или -1 чтобы не менять)\n"
                         f"• Медиа: + включить, - выключить, -1 не менять",
                         parse_mode='Markdown')
        userstates[user_id][chat_id] = 7
        setting_limits[user_id] = btn

    elif destiny == "changechan":
        userstates[user_id][chat_id] = 4
        bot.send_message(chat_id,
                         "🔄 *Смена канала*\n\n"
                         "🔑 Пожалуйста, пришлите новый токен канала...",
                         parse_mode='Markdown')

    elif destiny == "resend":
        if user_id not in current_tokens:
            bot.send_message(chat_id,
                             "📨 *Отправка сообщения*\n\n"
                             "🔑 Пожалуйста, пришлите токен канала...",
                             parse_mode='Markdown')
            userstates[user_id][chat_id] = 4
        else:
            chan_id = get_chan_id(user_id)
            if chan_id:
                if user_id not in waiting_users[chan_id]:
                    userstates[user_id][chat_id] = 5
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
                    bot.send_message(chat_id,
                                     f"✍️ *Готово к отправке!*\n\n"
                                     f"📢 Канал: `{bot.get_chat(chan_id).title}`\n\n"
                                     f"Напишите сообщение для отправки:",
                                     parse_mode='Markdown', reply_markup=markup)
                else:
                    userstates[user_id][chat_id] = 1
                    bot.send_message(chat_id,
                                     f"⏳ *Пожалуйста, подождите {limits[chan_id]['onemessper']} секунд*\n\n"
                                     f"Это необходимо для предотвращения спама.",
                                     parse_mode='Markdown')
            else:
                userstates[user_id][chat_id] = 1
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Попробовать другой токен", callback_data="wrongtok_-1"))
                bot.send_message(chat_id,
                                 "❌ *Токен недействителен!*\n\n"
                                 "Токен был изменён или удалён администратором.",
                                 parse_mode='Markdown', reply_markup=markup)

    elif destiny == "wrongtok":
        userstates[user_id][chat_id] = 4
        bot.send_message(chat_id,
                         "🔄 *Смена токена*\n\n"
                         "🔑 Пожалуйста, пришлите новый токен канала...",
                         parse_mode='Markdown')

    elif destiny == "complaint":
        if call.message.message_id not in complainted:
            if call.message.chat.id not in channels_where_admin:
                return False
            if check_is_admin(call.from_user.id, bot.get_chat_administrators(call.message.chat.id)):
                bot.reply_to(call.message, "⚠️ Жалоба отправлена на модерацию!")

            complainted.append(call.message.message_id)

            bot.answer_callback_query(call.id, "✅ Жалоба отправлена модерации")

            bot.send_message(6720238906,
                             f"⚠️ *Новая жалоба на сообщение*\n\n"
                             f"📢 Канал: {call.message.chat.title}\n"
                             f"👤 От: {call.from_user.first_name}\n"
                             f"📝 Текст: {call.message.text or 'Медиа-сообщение'}",
                             parse_mode='Markdown')

            bot.forward_message(6720238906, call.message.chat.id, call.message.message_id)

            def background_task():
                time.sleep(3600)
                if call.message.message_id in complainted:
                    complainted.remove(call.message.message_id)

            threading.Thread(target=background_task).start()

        else:
            bot.answer_callback_query(call.id, "⏳ Жалоба уже была отправлена на модерацию!")


bot.polling(none_stop=True)



