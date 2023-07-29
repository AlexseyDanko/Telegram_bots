import telebot
from telebot import types
import datetime
import re

TOKEN = 'Your token' #config.py == env
bot = telebot.TeleBot(TOKEN)

users_dict = {}  # Словарь для хранения информации о пользователях
user_groups = {}
groups_dict = {}
def create_menu_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('/StarT'),
        types.KeyboardButton('/SenD_To_GrouP'),
        types.KeyboardButton('/GrouPS'),
        types.KeyboardButton('/ADDGrouP'),
        types.KeyboardButton('/AllUserS'),
    )
    return keyboard

@bot.message_handler(commands=['StarT'])
def handle_start(message):
    if message.chat.id not in users_dict:
        user_info = f"Привет, {message.from_user.first_name}!"
        if message.from_user.username:
            user_info += f"\nТвой username: @{message.from_user.username}"

        users_dict[message.chat.id] = {
            'id': message.from_user.id,
            'username': message.from_user.username or message.from_user.first_name,
            'first_call': datetime.datetime.now(),
            'last_call': datetime.datetime.now(),  # Новое поле для хранения даты и времени последнего вызова
            'group_id': message.chat.id,  # Сохраняем ID группы из которой пользователь обратился впервые
        }

        bot.send_message(message.chat.id, user_info + " \nЯ бот KvizBy, давайте развивать бизнес!!", reply_markup=create_menu_buttons())
    else:
        # Если пользователь уже есть в users_dict, то обновляем информацию о последнем вызове и ID группы
        users_dict[message.chat.id]['last_call'] = datetime.datetime.now()
        users_dict[message.chat.id]['group_id'] = message.chat.id
        bot.send_message(message.chat.id, "С возвращением! Давайте продолжим развивать бизнес!", reply_markup=create_menu_buttons())

@bot.message_handler(commands=['SenD_To_GrouP'])
def handle_send_to_group(message):
    user_id = message.from_user.id
    user_groups = [{'link': group_link, 'added_by': group_info['added_by']} for group_link, group_info in groups_dict.items() if group_info['added_by'] == users_dict[user_id]['username']]

    if not user_groups:
        bot.send_message(message.chat.id, "Список групп пуст.", reply_markup=create_menu_buttons())
    else:
        bot.send_message(message.chat.id, "Выберите группу для отправки сообщения!", reply_markup=create_groups_keyboard(user_groups))
        bot.register_next_step_handler(message, process_group_message, user_groups)

def create_groups_keyboard(groups):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for group_info in groups:
        group_link = group_info['link']
        keyboard.add(types.KeyboardButton(group_link))
    return keyboard

def process_group_message(message, user_groups):
    try:
        selected_group_link = message.text.strip()
        selected_group_info = next((group for group in user_groups if group['link'] == selected_group_link), None)
        added_by = users_dict.get(message.chat.id)

        if selected_group_info and selected_group_link in groups_dict and groups_dict[selected_group_link]['added_by'] == added_by['username']:
            bot.send_message(message.chat.id, "Отправьте сообщение для отправки в выбранную группу:")
            bot.register_next_step_handler(message, send_to_selected_group, selected_group_link)
        else:
            bot.send_message(message.chat.id, "У Вас нет прав на редактирование Группы!", reply_markup=create_menu_buttons())

    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "Некорректный ввод. Пожалуйста, выберите группу из списка.", reply_markup=create_menu_buttons())

def send_to_selected_group(message, selected_group_link):
    if selected_group_link not in groups_dict:
        bot.send_message(message.chat.id, "Я не подключён к выбранной группе", reply_markup=create_menu_buttons())
    else:
        bot.send_message(groups_dict[selected_group_link]['id'], message.text)
        bot.send_message(message.chat.id, "Сообщение успешно отправлено!", reply_markup=create_menu_buttons())

@bot.message_handler(commands=['GrouPS'])
def handle_groups(message):
    groups_list = ""
    for group_link, group_info in groups_dict.items():
        added_by = group_info['added_by']
        date_added = group_info['date_added']
        groups_list += f"\nСсылка на группу: {group_link}\nДобавил: @{added_by}\nДата добавления: {date_added}\n"

    if groups_list:
        bot.send_message(message.chat.id, "Список групп:" + groups_list, reply_markup=create_menu_buttons())
    else:
        bot.send_message(message.chat.id, "Список групп пуст.", reply_markup=create_menu_buttons())

@bot.message_handler(commands=['ADDGrouP'])
def handle_add_group(message):
    bot.send_message(message.chat.id, "Отправьте мне ссылку на группу в формате https://t.me/TestTelegramBotu")
    bot.register_next_step_handler(message, process_group_link)

def process_group_link(message):
    group_link = message.text.strip()
    if re.match(r'https:\/\/t\.me\/[a-zA-Z0-9_]+$', group_link):
        if group_link not in groups_dict:
            added_by = users_dict.get(message.chat.id)
            if added_by:
                date_added = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                groups_dict[group_link] = {
                    'id': message.from_user.id,
                    'added_by': added_by['username'],
                    'date_added': date_added,
                }
                bot.send_message(message.chat.id, "Группа успешно добавлена!", reply_markup=create_menu_buttons())
            else:
                bot.send_message(message.chat.id, "К сожалению, не удалось определить ваш username. Попробуйте снова.")
        else:
            bot.send_message(message.chat.id, "Эта группа уже была добавлена ранее.", reply_markup=create_menu_buttons())
    else:
        bot.send_message(message.chat.id, "Неверный формат ссылки на группу. Попробуйте еще раз. Возможно Вы случайно нажали кнопку. Выберите команду заново! ", reply_markup=create_menu_buttons())

@bot.message_handler(commands=['AllUserS'])
def handle_all_users(message):
    users_list = ""
    for chat_id, user_info in users_dict.items():
        user_id = user_info['id']
        username = user_info['username']
        first_call = user_info['first_call'].strftime('%Y-%m-%d %H:%M:%S')
        last_call = user_info['last_call'].strftime('%Y-%m-%d %H:%M:%S')
        group_id = user_info['group_id']
        users_list += f"\nUser ID: {user_id}\n@{username}: Первый вызов {first_call}\nПоследний вызов {last_call}\nID Группы: {group_id}\n"

    if users_list:
        bot.send_message(message.chat.id, f"Список пользователей, которые меня запускали:\n{users_list}", reply_markup=create_menu_buttons())
    else:
        bot.send_message(message.chat.id, "Список пользователей пуст.", reply_markup=create_menu_buttons())

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id, "К сожалению, я не понимаю данную команду. Воспользуйтесь меню.", reply_markup=create_menu_buttons())

bot.polling()
