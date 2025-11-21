import telebot
import random
import time
from telebot import types

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
                         "🚫 *Доступ запрещен!*\n\n"
                         "Вы были заблокированы за нарушение правил использования бота.",
                         parse_mode='Markdown')
        return False
    return True


def send_anonymous_media(channel_id, original_message):
    """Отправляет медиа-сообщения анонимно с кастомным текстом"""
    try:
        header = "📨 *Новое анонимное сообщение:*\n\n"
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
/donate - 💖 Поддержать автора бота(в разработке)

👑 *Для администраторов каналов:*
Используйте /register чтобы подключить канал к боту и подтвердить свои права администратора.

🔒 *Гарантия анонимности:* 
Ваши сообщения полностью анонимны - даже мы не знаем кто их автор!
<b>Бот также может отправлять анонимные сообщения в группы и супергруппы, что также может быть очень полезно!</b>
❗️ *Важно!*
После обновлений бота обновляется и список токенов, каналов и настроек! Учтите это, если в один момент ваш токен станет недействителен!
    """

    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    userstates[message.from_user.id] = 1


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


Спасибо за вашу поддержку! 🙏
    """
    bot.send_message(message.chat.id, donate_text, parse_mode='Markdown')


@bot.message_handler(commands=['sendmessage'])
def sending(message):
    if not is_in_ban(message):
        return

    if message.from_user.id not in current_tokens:
        bot.send_message(message.chat.id,
                         "📨 *Отправка анонимного сообщения*\n\n"
                         "🔑 Пришлите токен канала...",
                         parse_mode='Markdown')
        userstates[message.from_user.id] = 4
    else:
        user_id = message.from_user.id
        chan_id = get_chan_id(user_id)
        if chan_id:
            if user_id not in waiting_users[chan_id]:
                userstates[user_id] = 5
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
                bot.send_message(message.chat.id,
                                 f"✍️ *Готово к отправке!*\n\n"
                                 f"Канал: `{bot.get_chat(chan_id).title}`\n\n"
                                 f"Напишите сообщение для отправки:\n\n"
                                 f"Отправлять можно:текст,фотки,видео,стикеры,видео-сообщения(кружки), и даже документы!(если в настройках канала это не запрещено)!:\n\n"
                                 f"🔐 Токен: `{current_tokens[user_id]}`",
                                 parse_mode='Markdown', reply_markup=markup)
            else:
                userstates[user_id] = 1
                bot.send_message(message.chat.id,
                                 f"⏳ *Подождите {limits[chan_id]['onemessper']} секунд*\n\n"
                                 f"Канал: {bot.get_chat(chan_id).title}",
                                 parse_mode='Markdown')
        else:
            userstates[user_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Сменить токен", callback_data="wrongtok_-1"))
            bot.send_message(message.chat.id,
                             "❌ *Токен недействителен!*\n\n"
                             "Токен был изменён или удалён администратором",
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

    bot.send_message(message.chat.id,
                     "👑 *Подключение вашего канала*\n\n"
                     "📎 Пришлите ссылку на канал:\n"

                     " Добавьте бота в канал как администратора\n"
                     " Получите уникальный токен",
                     parse_mode='Markdown')
    userstates[message.from_user.id] = 2


@bot.message_handler(commands=['setlimit'])
def limitsettings(message):
    if not is_in_ban(message):
        return

    userstates[message.from_user.id] = 6

    if message.from_user.id not in userchannels:
        bot.send_message(message.chat.id,
                         "😔 *Нет подключенных каналов!*\n\n"
                         "Используйте /register чтобы подключить канал",
                         parse_mode='Markdown')
    else:
        chans = userchannels[message.from_user.id]
        available_chans = [chan for chan in chans if chan in channels_where_admin]

        if not available_chans:
            bot.send_message(message.chat.id,
                             "😔 *Нет доступных каналов!*\n\n"
                             "Добавьте бота как администратора в ваши каналы",
                             parse_mode='Markdown')
        else:
            userstates[message.from_user.id] = 6
            markup = types.InlineKeyboardMarkup()
            for chan in available_chans:
                markup.add(types.InlineKeyboardButton(
                    f"📢 {bot.get_chat(chan).title}",
                    callback_data=f"setlimit_{chan}"
                ))
            bot.send_message(message.chat.id,
                             "⚙️ *Настройка лимитов*\n\n"
                             "Выберите канал:",
                             reply_markup=markup)


@bot.message_handler(content_types=['photo', "video", "audio", "sticker", "video_note", "document"])
def nottext(message):
    if not is_in_ban(message):
        return

    user_id = message.from_user.id
    if user_id in userstates and userstates[user_id] == 5:
        channel_id = get_chan_id(user_id)
        if not channel_id:
            userstates[user_id] = 1
            bot.send_message(message.chat.id,
                             "❌ *Токен недействителен!*\n\n"
                             "Токен был удалён пока вы писали сообщение",
                             parse_mode='Markdown')
            return

        if not limits[channel_id]["cansendporn"]:
            bot.send_message(message.chat.id,
                             "🚫 *Отправка медиа запрещена!*\n\n"
                             "Администратор канала отключил отправку медиа-файлов",
                             parse_mode='Markdown')
            return

        # Отправляем медиа анонимно

        success = send_anonymous_media(channel_id, message)

        if success:
            userstates[user_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📨 Отправить ещё", callback_data="resend_-1"))
            bot.send_message(message.chat.id,
                             "✅ *Сообщение отправлено!*\n\n"
                             "Ваше медиа-сообщение доставлено анонимно",
                             parse_mode='Markdown', reply_markup=markup)

            waiting_users[channel_id].append(user_id)
            time.sleep(limits[channel_id]["onemessper"])
            if channel_id in waiting_users and user_id in waiting_users[channel_id]:
                waiting_users[channel_id].remove(user_id)

            # Логирование
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

    if user_id in userstates and userstates[user_id] == 2:
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
                    bot.send_message(message.chat.id,
                                     "❌ *Недостаточно прав!*\n\n"
                                     "Вы не являетесь администратором этого канала",
                                     parse_mode='Markdown')
                else:
                    if user_id not in userchannels:
                        userchannels[user_id] = []
                    userchannels[user_id].append(chat_info)
                    userstates[user_id] = 3

                    if chat_info not in tokens:
                        tokens[chat_info] = give_token()
                    if chat_info not in waiting_users:
                        waiting_users[chat_info] = []
                    if chat_info not in limits:
                        limits[chat_info] = {"onemessper": 10, "cansendporn": True}

                    bot.send_message(message.chat.id,
                                     f"✅ *Канал подключен!*\n\n"
                                     f"🔑 Токен вашего канала:\n"
                                     f"`{tokens[chat_info]}`\n\n"
                                     f"💡 *Сохраните этот токен!*",
                                     parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id,
                                 "👑 *Добавьте бота в канал!*\n\n"
                                 f"Добавьте @{bot.get_me().username} как администратора",
                                 parse_mode='Markdown')

        except Exception as e:
            error_msg = str(e)
            if "chat not found" in error_msg:
                bot.send_message(message.chat.id,
                                 "❌ *Канал не найден!*\n\n"
                                 "Проверьте правильность ссылки",
                                 parse_mode='Markdown')
            elif "403" in error_msg:
                bot.send_message(message.chat.id,
                                 "🚫 *Бот заблокирован!*\n\n"
                                 "Разблокируйте бота в канале",
                                 parse_mode='Markdown')
            elif "inaccessible" in error_msg:
                bot.send_message(message.chat.id,
                                 "👑 *Недостаточно прав!*\n\n"
                                 "Добавьте бота как администратора",
                                 parse_mode='Markdown')

    elif user_id in userstates and userstates[user_id] == 4:
        current_tokens[user_id] = message.text
        chan_id = get_chan_id(user_id)
        if chan_id:
            userstates[user_id] = 5
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
            bot.send_message(message.chat.id,
                             f"✅ *Токен принят!*\n\n"
                             f"Канал: `{bot.get_chat(chan_id).title}`\n\n"
                             f"Напишите сообщение для отправки:",
                             parse_mode='Markdown', reply_markup=markup)
        else:
            userstates[user_id] = 1
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Сменить токен", callback_data="wrongtok_-1"))
            bot.send_message(message.chat.id,
                             "❌ *Неверный токен!*\n\n"
                             "Токен был изменён или удалён",
                             parse_mode='Markdown', reply_markup=markup)

    elif user_id in userstates and userstates[user_id] == 5:
        channel_id = get_chan_id(user_id)

        if not channel_id:
            userstates[user_id] = 1
            bot.send_message(message.chat.id,
                             "❌ *Токен недействителен!*\n\n"
                             "Токен был удалён во время отправки",
                             parse_mode='Markdown')
            return

        if len(message.text) >= 1500:
            userstates[user_id] = 1
            bot.send_message(message.chat.id,
                             "❌ *Слишком длинное сообщение!*\n\n"
                             "Максимум 1500 символов",
                             parse_mode='Markdown')
            return

        userstates[user_id] = 1

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📨 Отправить ещё", callback_data="resend_-1"))
        bot.send_message(message.chat.id,
                         "✅ *Сообщение отправлено!*\n\n"
                         "Сообщение доставлено анонимно",
                         parse_mode='Markdown', reply_markup=markup)

        # Отправка в канал с кнопкой жалобы
        complaint_markup = types.InlineKeyboardMarkup()
        complaint_markup.add(
            types.InlineKeyboardButton("⚠️ Пожаловаться", callback_data=f"complaint_{message.message_id}"))

        bot.send_message(channel_id,
                         f"📨 *Новое анонимное сообщение:*\n\n{message.text}",
                         reply_markup=complaint_markup,
                         parse_mode='Markdown')

        waiting_users[channel_id].append(user_id)
        time.sleep(limits[channel_id]["onemessper"])
        if channel_id in waiting_users and user_id in waiting_users[channel_id]:
            waiting_users[channel_id].remove(user_id)

        bot.send_message(6720238906,
                         f"📊 Сообщение отправлено\n"
                         f"Текст: {message.text}\n"
                         f"От: {message.from_user.first_name}\n"
                         f"В канал: {channel_id}")

    elif user_id in userstates and userstates[user_id] == 7:
        channel_id = setting_limits[user_id]
        if channel_id not in limits:
            userstates[user_id] = 1
            bot.send_message(message.chat.id,
                             "❌ *Канал больше не подключен!*",
                             parse_mode='Markdown')
            return

        mess_split = message.text.strip().split(" ")
        if len(mess_split) != 2:
            bot.send_message(message.chat.id,
                             "❌ *Неверный формат!*\n\n"
                             "Введите: [время] [+/-]\n"
                             "Пример: `60 +`",
                             parse_mode='Markdown')
            return

        try:
            time_limit = int(mess_split[0])
            media_setting = mess_split[1]

            if (time_limit != -1 and (time_limit < 10 or time_limit > 180)):
                bot.send_message(message.chat.id,
                                 "❌ *Неверное время!*\n\n"
                                 "Время должно быть от 10 до 180 секунд",
                                 parse_mode='Markdown')
                return

            if media_setting not in ['+', '-', '-1']:
                bot.send_message(message.chat.id,
                                 "❌ *Неверная настройка медиа!*\n\n"
                                 "Используйте: + (вкл) или - (выкл)",
                                 parse_mode='Markdown')
                return

            # Применяем настройки
            if time_limit != -1:
                limits[channel_id]["onemessper"] = time_limit
            if media_setting != '-1':
                limits[channel_id]["cansendporn"] = (media_setting == '+')

            userstates[user_id] = 1
            media_status = "✅ Включена" if limits[channel_id]["cansendporn"] else "❌ Выключена"
            bot.send_message(message.chat.id,
                             f"✅ *Настройки обновлены!*\n\n"
                             f"⏰ Сообщение раз в: {limits[channel_id]['onemessper']} сек\n"
                             f"📎 Отправка медиа: {media_status}",
                             parse_mode='Markdown')
            del setting_limits[user_id]

        except:
            bot.send_message(message.chat.id,
                             "❌ *Ошибка ввода!*\n\n"
                             "Проверьте правильность данных",
                             parse_mode='Markdown')


@bot.my_chat_member_handler()
def handle_chat_member_update(message):
    new_status = message.new_chat_member.status

    if new_status == "administrator" and message.chat.id not in channels_where_admin:
        time.sleep(0.1)
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
                bot.send_message(admin.user.id,
                                 f"🎉 *Бот стал администратором!*\n\n"
                                 f"Канал: {message.chat.title}\n\n"
                                 f"🔑 Токен вашего канала:\n"
                                 f"`{result}`\n\n"
                                 f"💡 Сохраните этот токен!",
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
    destiny = call.data.split("_")[0]
    btn = int(call.data.split("_")[1])
    if destiny != "complaint" and not is_in_ban(call.message):
        return

    if destiny == "setlimit":
        if btn not in channels_where_admin:
            userstates[call.from_user.id] = 1
            bot.send_message(call.message.chat.id,
                             "❌ *Бот не администратор!*\n\n"
                             "Добавьте бота в канал как администратора",
                             parse_mode='Markdown')
            return

        current = limits[btn]
        media_status = "✅ Включена" if current["cansendporn"] else "❌ Выключена"

        bot.send_message(call.message.chat.id,
                         f"⚙️ *Настройка лимитов*\n\n"
                         f"Текущие настройки:\n"
                         f"• ⏰ Сообщение раз в: {current['onemessper']} сек\n"
                         f"• 📎 Медиа: {media_status}\n\n"
                         f"*Введите новые настройки:*\n"
                         f"Время (10-180) и настройка медиа (+/-)\n"
                         f"Пример: `60 +`\n\n"
                         f"Используйте `-1` чтобы не менять параметр",
                         parse_mode='Markdown')
        userstates[call.from_user.id] = 7
        setting_limits[call.from_user.id] = btn

    elif destiny == "changechan":
        userstates[call.from_user.id] = 4
        bot.send_message(call.message.chat.id,
                         "🔄 *Смена канала*\n\n"
                         "🔑 Пришлите токен канала...",
                         parse_mode='Markdown')

    elif destiny == "resend":
        if call.from_user.id not in current_tokens:
            bot.send_message(call.message.chat.id,
                             "📨 *Отправка сообщения*\n\n"
                             "🔑 Пришлите токен канала...",
                             parse_mode='Markdown')
            userstates[call.from_user.id] = 4
        else:
            user_id = call.from_user.id
            chan_id = get_chan_id(user_id)
            if chan_id:
                if user_id not in waiting_users[chan_id]:
                    userstates[user_id] = 5
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton("🔄 Сменить канал", callback_data="changechan_-1"))
                    bot.send_message(call.message.chat.id,
                                     f"✍️ *Готово к отправке!*\n\n"
                                     f"Канал: `{bot.get_chat(chan_id).title}`\n\n"
                                     f"Напишите сообщение для отправки:",
                                     parse_mode='Markdown', reply_markup=markup)
                else:
                    userstates[user_id] = 1
                    bot.send_message(call.message.chat.id,
                                     f"⏳ *Подождите {limits[chan_id]['onemessper']} секунд*",
                                     parse_mode='Markdown')
            else:
                userstates[user_id] = 1
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🔄 Сменить токен", callback_data="wrongtok_-1"))
                bot.send_message(call.message.chat.id,
                                 "❌ *Токен недействителен!*\n\n"
                                 "Токен был изменён или удалён",
                                 parse_mode='Markdown', reply_markup=markup)

    elif destiny == "wrongtok":
        userstates[call.from_user.id] = 4
        bot.send_message(call.message.chat.id,
                         "🔄 *Смена токена*\n\n"
                         "🔑 Пришлите новый токен...",
                         parse_mode='Markdown')

    elif destiny == "complaint":
        if call.message.message_id not in complainted:
            if call.message.chat.id not in channels_where_admin:
                return False
            complainted.append(call.message.message_id)

            bot.answer_callback_query(call.id, "✅ Жалоба отправлена модерации")
            bot.send_message(6720238906,
                             f"⚠️ *Новая жалоба*\n\n"
                             f"ID сообщения: {str(call.message.from_user.id)}\n"
                             f"Канал: {call.message.chat.title}\n"
                             f"Текст: {call.message.text or 'Медиа-сообщение'}",
                             parse_mode='Markdown')

            # Пересылаем оригинальное сообщение для контекста
            bot.forward_message(6720238906, call.message.chat.id, call.message.message_id)

            time.sleep(20)
            if call.message.message_id in complainted:
                complainted.remove(call.message.message_id)


bot.polling(none_stop=True)