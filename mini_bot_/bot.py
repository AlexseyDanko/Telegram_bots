import telebot


TOKEN = 'your bot token'
bot = telebot.TeleBot(TOKEN)


groups_and_owners = {
    'TestGroup': 2031814734,  # name group and id_owner
    'TestTelegramBot': 2031814734,  # name group and id_owner
   
}


group_links = {
    'TestGroup': 'https://t.me/',#your links group
    'TestTelegramBot': 'https://t.me/',#your links group
    
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    first_name = user.first_name
    last_name = user.last_name
    user_id = user.id

    response = f"Привет, {first_name} {last_name} (ID: {user_id})!"

    if message.chat.type == 'supergroup':
        group_id = message.chat.id
        response += f"\nВы находитесь в супергруппе с ID: {group_id}"

    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['send_to_group'])
def send_to_group(message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        allowed_groups = [group_name for group_name, owner_id in groups_and_owners.items() if user_id == owner_id]

        if allowed_groups:
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for group_name in allowed_groups:
                markup.add(group_name)

            msg = bot.send_message(message.chat.id, "Выберите группу, в которую хотите отправить сообщение:", reply_markup=markup)
            bot.register_next_step_handler(msg, process_group_selection)
        else:
            bot.send_message(message.chat.id, "Вы не являетесь владельцем ни одной из указанных групп.")
    else:
        bot.send_message(message.chat.id, "Эта команда доступна только в личных сообщениях бота.")

def process_group_selection(message):
    user_id = message.from_user.id
    selected_group = message.text

    if selected_group in groups_and_owners.keys() and user_id == groups_and_owners[selected_group]:
        bot.send_message(message.chat.id, "Введите сообщение для отправки в выбранную группу:")
        bot.register_next_step_handler(message, process_message)
    else:
        bot.send_message(message.chat.id, "Ошибка: вы не являетесь владельцем выбранной группы или такой группы не существует.")

def process_message(message):
    user_id = message.from_user.id
    selected_group = message.text
    if selected_group in groups_and_owners.keys() and user_id == groups_and_owners[selected_group]:
        message_text = message.text
        if len(message_text) < 4096:
            bot.send_message(groups_and_owners[selected_group], message_text)
        else:
            send_large_message_in_parts(groups_and_owners[selected_group], message_text)
    else:
        bot.send_message(message.chat.id, "Ошибка: вы не являетесь владельцем выбранной группы или такой группы не существует.")

def send_large_message_in_parts(chat_id, message_text):
    max_message_length = 4096
    for i in range(0, len(message_text), max_message_length):
        bot.send_message(chat_id, message_text[i:i + max_message_length])

@bot.message_handler(commands=['help'])
def show_help(message):
    help_message = "Список доступных команд:\n" \
                   "/start - Вывести приветственное сообщение и информацию о пользователе\n" \
                   "/send_to_group - Отправить сообщение в одну из групп, в которой вы являетесь владельцем\n" \
                   "/help - Вывести список доступных команд\n" \
                   "/groups - Вывести список групп (ссылки), доступных вам как владельцу\n"

    bot.send_message(message.chat.id, help_message)

@bot.message_handler(commands=['groups'])
def show_groups(message):
    user_id = message.from_user.id
    allowed_groups = [group_name for group_name, owner_id in groups_and_owners.items() if user_id == owner_id]

    if allowed_groups:
        groups_list = "\n".join(f"{group_name}: {group_links[group_name]}" for group_name in allowed_groups)
        bot.send_message(message.chat.id, f"Список доступных вам групп:\n{groups_list}")
    else:
        bot.send_message(message.chat.id, "Вы не являетесь владельцем ни одной из указанных групп.")

bot.polling()
