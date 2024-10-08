import os
import traceback
import telebot
import sqlite3
from dotenv import load_dotenv

from telebot import types

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)
DBNAME = os.getenv('DBNAME')

REMOVE_BUTTON_SETTING = telebot.types.ReplyKeyboardRemove()


def create_fake_user(name, tg_id, username):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, tg_id, username) VALUES ('%s', '%d', '%s')" % (
            name, tg_id, username)
    )
    conn.commit()

    cur.close()
    conn.close()


def create_friend_for_user(user_id, friend_id, status):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO friend_list (user_id, friend_id, friend_status) VALUES ('%d', '%d', '%s')" % (
            user_id, friend_id, status)
    )
    conn.commit()

    cur.close()
    conn.close()


def create_table():
    print('Функция создания БД')
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(10), tg_id int, username varchar(50), chat_id int)'
    )
    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS friend_list (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id int, friend_id int, friend_status varchar(20))'
    )
    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS event_list (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(100), time_and_date varchar(50), place varchar(100), info varchar(511), creator_id int, event_status varchar(20))'
    )
    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS friend_response_to_event (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id int, user_id int, is_creator bool, response_status varchar(20), info_from_user varchar(255))'
    )

    conn.commit()

    cur.close()
    conn.close()


def create_user(message):
    print('Работает функция создания пользвоателя')
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    name = message.text.strip()

    tg_id = message.from_user.id
    username = str(message.from_user.username).strip()

    if username != 'None':
        username = '@' + username

    cur.execute(
        "INSERT INTO users (name, tg_id, username, chat_id) VALUES ('%s', '%d', '%s', '%d')" % (
        name, tg_id, username, message.chat.id)
    )
    conn.commit()

    cur.execute(
        'select * from users'
    )
    # conn.commit()
    # возвращает все найденные записи
    users = cur.fetchall()
    #
    info = ''
    for el in users:
        info += f'Имя {el[0]}\n'
        print(el[0], el[1])
        print(el)
    # bot.send_message(message.chat.id, info)
    print(list(users))
    bot.send_message(message.chat.id,
                     f'Теперь ваши друзья будут видеть вас под именем: {name}.\n\nЭто имя можно будет изменить в будущем')
    cur.close()
    conn.close()

    create_main_menu(message)


def create_main_menu(message):
    print('Создал меню')
    # bot.send_message(message.chat.id, 'Что тебе интересно?')
    markup = types.ReplyKeyboardMarkup()
    # btn1 = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Создать мероприятие')
    btn2 = types.KeyboardButton('Мои мероприятия')
    markup.row(btn1)
    markup.row(btn2)
    btn3 = types.KeyboardButton('Профиль')
    btn4 = types.KeyboardButton('Заявки в друзья')
    markup.row(btn3, btn4)
    # bot.edit_message_reply_markup(message.chat.id, reply_markup=markup)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    # bot.set_chat_menu_button(message.chat.id, markup)
    bot.register_next_step_handler(message, on_click_main_menu)


def create_profile_menu(message):
    print('Создал меню профиля')
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Список друзей')
    btn6 = types.KeyboardButton('Заявки в друзья')
    btn2 = types.KeyboardButton('Добавить в друзья')
    btn5 = types.KeyboardButton('Удалить из друзей')
    markup.row(btn1, btn6)
    markup.row(btn2, btn5)
    btn3 = types.KeyboardButton('Изменить отображаемое имя')
    btn4 = types.KeyboardButton('Назад в меню')
    markup.row(btn3)
    markup.row(btn4)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    # bot.set_chat_menu_button(message.chat.id, markup)
    bot.register_next_step_handler(message, on_click_profile_menu)


def check_user_by_id(invite_friend_id):
    # print('Работает функция проверки')
    # create_table()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'select count(*) from users where id = %d' % (invite_friend_id)
    )
    # conn.commit()
    # возвращает все найденные записи
    count_accounts = cur.fetchall()
    #
    # print('Количество аккаунтов пользователя: ', count_accounts[0])

    cur.close()
    conn.close()
    if list(count_accounts[0])[0] > 0:
        return True
    else:
        return False


def check_invite_status(my_id, invite_friend_id, status):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'select friend_status from friend_list where user_id = %d and friend_id = %d' % (invite_friend_id, my_id)
    )
    friend_status = cur.fetchall()
    cur.close()
    conn.close()
    print('FFFFF')
    if friend_status == []:
        return False
    if friend_status[0][0] == status:
        return True
    else:
        return False


def check_friend(my_id, invite_friend_id):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'select id from friend_list where user_id = %d and friend_id = %d' % (invite_friend_id, my_id)
    )
    friend_status = cur.fetchall()
    cur.close()
    conn.close()
    print('FFFFF')
    if friend_status == []:
        return False
    # if friend_status[0][0] == status:
    #     return True
    else:
        return True


def add_to_friend(message):
    invite_friend_id = message.text
    try:
        invite_friend_id = int(invite_friend_id)

        my_id = get_id_from_database(message)
    except:
        print('Ошибка:\n', traceback.format_exc())
        bot.send_message(message.chat.id, 'ID друга - должно быть числом')
        create_profile_menu(message)
        return 0
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    print(my_id, invite_friend_id)

    if check_user_by_id(invite_friend_id) is False:
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Пользователь с данным ID не найден')
        create_profile_menu(message)
        return 0

    friend_status = check_friend(my_id, invite_friend_id)
    my_status = check_friend(invite_friend_id, my_id)

    if friend_status is True:
        cur.execute(
            'update friend_list set friend_status = "%s" where user_id = %d and friend_id = %d' % (
                'invite', invite_friend_id, my_id)
        )
    else:
        cur.execute(
            "INSERT INTO friend_list (user_id, friend_id, friend_status) VALUES ('%d', '%d', '%s')" % (
                invite_friend_id, my_id, 'invite')
        )
    if my_status is True:
        cur.execute(
            'update friend_list set friend_status = "%s" where user_id = %d and friend_id = %d' % (
                'wait_invite', my_id, invite_friend_id)
        )
    else:
        cur.execute(
            "INSERT INTO friend_list (user_id, friend_id, friend_status) VALUES ('%d', '%d', '%s')" % (
                my_id, invite_friend_id, 'wait_invite')
        )
    #
    # cur.execute(
    #     'update friend_list set friend_status = "%s" where user_id = %d and friend_id = %d' % (
    #         'invite', invite_friend_id, my_id)
    # )

    conn.commit()

    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Заявка в друзья отправлена')
    create_profile_menu(message)

    # tg_id = get_tg_id_from_database(invite_friend_id)

    print(type(invite_friend_id))
    # if type(invite_friend_id) !=
    # invite_tg_id = get_tg_id_from_database(invite_friend_id)


def on_click_profile_menu(message):
    if message.text == 'Назад в меню':
        create_main_menu(message)
    if message.text == 'Список друзей':
        get_friend_list(message)
        bot.register_next_step_handler(message, on_click_profile_menu)
    if message.text == 'Заявки в друзья':
        get_friend_invite(message)
    if message.text == 'Добавить в друзья':
        bot.send_message(message.chat.id, 'Попросите вашего друга сообщить ID\nВведите ID друга:')
        # print(message.text)
        bot.register_next_step_handler(message, add_to_friend)
        # add_friend(message, friend_info_id, 'invite')
        # get_friend_invite(message)
    if message.text == 'Удалить из друзей':
        bot.send_message(message.chat.id, 'Выберите друга, которого хотите удалить')
        get_friend_list(message)
        bot.register_next_step_handler(message, on_click_profile_menu)
    # bot.delete_message(message.chat.id, message.message_id - 1)
    # bot.delete_message(message.chat.id, message.message_id)


def get_friend_invite(message):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.from_user.id

    cur.execute(
        'select distinct TBL2.name, user_id, friend_id, TBL1.name, friend_status from friend_list as TBL left join users as TBL1 on TBL.friend_id = TBL1.id left join users as TBL2 on TBL2.id = TBL.user_id where TBL2.tg_id = %d and friend_status = "invite"' % (
            user_tg_id)
    )

    friend_list = cur.fetchall()

    markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton('Тест', callback_data='delete'))

    friend_list_txt = ''

    for friend in friend_list:
        print(friend[2], friend[3])
        friend_list_txt += f'ID: {friend[2]} Имя: {friend[3]}\n'
        markup.add(
            types.InlineKeyboardButton(f'ID: {friend[2]} | Имя: {friend[3]}\n', callback_data=f'add_menu{friend[2]}'))

    if friend_list_txt == '':
        friend_list_txt = 'Список заявок пуст(\nДрузья могут отсылать вам заявки по ID'
        bot.send_message(message.chat.id, friend_list_txt)
        create_profile_menu(message)
    else:
        bot.send_message(message.chat.id, 'С вами хотят подружиться:\n', reply_markup=markup)
        bot.register_next_step_handler(message, on_click_profile_menu)
    cur.close()
    conn.close()


def get_info_about_event_by_id(event_id):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    event_info_dict = {
        'id': event_id,
        'name': '',
        'time_and_date': '',
        'place': '',
        'info': '',
        'creator_id': '',
    }

    cur.execute(
        'select * from event_list where id = %d' % (event_id)
    )

    event_info = cur.fetchall()[0]

    # i = 0

    for number, key in enumerate(event_info_dict):
        event_info_dict[key] = event_info[number]

    print(event_info_dict)

    # print(event_info)
    cur.close()
    conn.close()
    print(event_info[0])
    return event_info_dict


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    # print(callback.data)
    # print(str(callback.data).replace('delete_menu', '').strip().isdigit())
    number_delete = str(callback.data).replace('delete_menu', '').strip()
    number_add = str(callback.data).replace('add_menu', '').strip()
    number_event = str(callback.data).replace('event_menu', '').strip()
    print(callback.data)
    if 'invite_friend_to_event' in callback.data and '_cancel' not in callback.data:
        number_friend_to_invite = str(callback.data).replace('invite_friend_to_event', '|').strip()
        event_id_for_invite, user_id_for_invite = number_friend_to_invite.split('|')
        print(event_id_for_invite, user_id_for_invite,
              event_id_for_invite + 'invite_friend_to_event' + user_id_for_invite)
    if callback.data == 'add_menu' + number_add:
        # print(callback.message)
        # bot.send_message(callback.message.chat.id, callback)
        # friend_info = callback.message.json['reply_markup']['inline_keyboard'][0][0]['text']
        # print(friend_info)
        # friend_info_array = friend_info.split('|')
        # friend_info_id = int(friend_info_array[0].replace('ID:', '').strip())

        friend_info_id = int(number_add)

        invite_text = f'Выбран друг:\n{number_add} \nДобавить в друзья?'

        markup = types.ReplyKeyboardMarkup()

        btn1 = types.KeyboardButton('Принять заявку')
        btn2 = types.KeyboardButton('Отклонить заявку')
        btn3 = types.KeyboardButton('Отмена')

        markup.row(btn1)
        markup.row(btn2)
        markup.row(btn3)

        bot.send_message(callback.message.chat.id, invite_text, reply_markup=markup)
        bot.register_next_step_handler(callback.message, on_click_menu_confirmation, friend_info_id=friend_info_id)
    elif callback.data == 'delete_menu' + number_delete:
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Удалить пользователя из друзей')
        btn2 = types.KeyboardButton('Отмена')
        markup.row(btn1)
        markup.row(btn2)
        friend_info_id = int(number_delete)
        invite_text = f'Выбран друг:\n{friend_info_id} \n'
        bot.send_message(callback.message.chat.id, invite_text, reply_markup=markup)
        bot.register_next_step_handler(callback.message, on_click_menu_confirmation, friend_info_id=friend_info_id)
    elif callback.data == 'event_menu' + number_event:
        print('event menu')
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Пригласить друзей')
        btn2 = types.KeyboardButton('Удалить мероприятие')
        btn3 = types.KeyboardButton('Отмена')
        btn4 = types.KeyboardButton('Подробнее о мероприятии')
        markup.row(btn1)
        markup.row(btn4)
        markup.row(btn2)
        markup.row(btn3)
        event_id = int(number_event)
        event_info_dict = get_info_about_event_by_id(event_id)
        invite_text = (f'Выбрано мероприятие:\n{event_info_dict["name"]} \n'
                       f'\nДата и время мероприятия:\n{event_info_dict["time_and_date"]}')
        bot.send_message(callback.message.chat.id, invite_text, reply_markup=markup)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.register_next_step_handler(callback.message, on_click_event_menu_confirmation, event_id=event_id)
    elif callback.data == 'event_cancel_menu':
        # bot.delete_message(callback.message.chat.id, callback.message.message_id - 2)
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        create_event_type_menu(callback.message)
    elif callback.data == 'invite_friend_to_event_cancel':
        # bot.send_message()
        # bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
        # bot.delete_message(callback.message.chat.id, callback.message.message_id)
        get_event_list_create_by_me_by_chat_id(callback.message)
        # print('Тут')
    elif callback.data == event_id_for_invite + 'invite_friend_to_event' + user_id_for_invite:
        print('Выбран друг ' + user_id_for_invite)
        invite_status = check_invite_friend_to_event(callback.message, event_id_for_invite, user_id_for_invite)
        print(invite_status)
        if invite_status is False:
            invite_friend_to_event(callback.message, event_id_for_invite, user_id_for_invite)

            markup = types.ReplyKeyboardMarkup()
            btn1 = types.KeyboardButton('Да')
            btn2 = types.KeyboardButton('Отмена')
            markup.row(btn1)
            markup.row(btn2)

            bot.send_message(callback.message.chat.id, 'Приглашение отправлено\nПригласить ещё кого-нибудь?',
                             reply_markup=markup)
            bot.register_next_step_handler(callback.message, on_click_menu_invite_again,
                                           event_id_for_invite=event_id_for_invite)
            # bot.send_message()
            # bot.send_message(callback.message.chat.id, 'Давайте пригласим ещё друзей')
            # print(callback.message)
            # choice_friend_for_event(callback.message, event_id_for_invite)
            # callback_message(callback.data)
        else:
            # bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
            bot.send_message(callback.message.chat.id, 'Данный пользователь уже приглашён на мероприятие')
            choice_friend_for_event(callback.message, event_id_for_invite)
            # get_event_list_create_by_me_by_chat_id(callback.message)
            # print(callback.message)
            # choice_friend_for_event(callback.message, event_id_for_invite)


def on_click_menu_invite_again(message, event_id_for_invite):
    if message.text == 'Да':
        choice_friend_for_event(message, event_id_for_invite)


def check_invite_friend_to_event(message, event_id_for_invite, number_friend_to_invite):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    print(event_id_for_invite, number_friend_to_invite)
    cur.execute(
        'select count(*) from friend_response_to_event where event_id = %d and user_id = %d' % (
        int(event_id_for_invite), int(number_friend_to_invite))
    )
    # conn.commit()
    # возвращает все найденные записи
    have_invite = cur.fetchall()
    #
    print('Количество аккаунтов пользователя: ', have_invite)

    cur.close()
    conn.close()
    if list(have_invite[0])[0] > 0:
        return True
    else:
        return False


def invite_friend_to_event(message, event_id_for_invite, user_id_for_invite):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    friend_from_info = (int(event_id_for_invite), int(user_id_for_invite), False, 'wait status', '')

    cur.execute(
        "INSERT INTO friend_response_to_event (event_id, user_id, is_creator, response_status, info_from_user) VALUES ('%d', '%d', '%r', '%s', '%s')" % tuple(
            friend_from_info)
    )

    conn.commit()

    cur.close()
    conn.close()


def create_actions_for_event_menu(message, event_id):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Пригласить друзей')
    btn2 = types.KeyboardButton('Удалить мероприятие')
    btn3 = types.KeyboardButton('Отмена')
    btn4 = types.KeyboardButton('Подробнее о мероприятии')
    markup.row(btn1)
    markup.row(btn4)
    markup.row(btn2)
    markup.row(btn3)
    event_id = int(event_id)
    bot.register_next_step_handler(message, on_click_event_menu_confirmation, event_id=event_id)


def on_click_event_menu_confirmation(message, event_id):
    if message.text == 'Отмена':
        # bot.delete_message(message.chat.id, message.message_id - 3)
        # bot.delete_message(message.chat.id, message.message_id - 2)
        # bot.delete_message(message.chat.id, message.message_id - 1)
        get_event_list_create_by_me_by_chat_id(message)
    if message.text == 'Удалить мероприятие':
        # bot.send_message(message.chat.id, event_id)

        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        cur.execute(
            'DELETE FROM event_list WHERE id = %d' % (event_id)
        )

        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Мероприятие удалено')
        get_event_list_create_by_me_by_chat_id(message)
    if message.text == 'Подробнее о мероприятии':
        event_info = get_info_about_event_by_id(event_id)
        print('-' * 20)
        print(event_info)
        event_info_txt = f'ID события: {event_info["id"]}\n\nНазвание мероприятия:\n{event_info["name"]}\n\nВремя и дата мероприятия:\n{event_info["time_and_date"]}\n\nДополнительная информафия:\n{event_info["info"]}'
        bot.send_message(message.chat.id, event_info_txt)
        create_actions_for_event_menu(message, event_id)
    if message.text == 'Пригласить друзей':
        choice_friend_for_event(message, event_id)


def choice_friend_for_event(message, event_id):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.chat.id  # message.from_user.id

    cur.execute(
        'select distinct TBL2.name, user_id, friend_id, TBL1.name, friend_status from friend_list as TBL left join users as TBL1 on TBL.friend_id = TBL1.id left join users as TBL2 on TBL2.id = TBL.user_id where TBL2.tg_id = %d and friend_status = "friend"' % (
            user_tg_id)
    )

    friend_for_invite_to_event = cur.fetchall()
    markup = types.InlineKeyboardMarkup()
    friend_list_txt = ''
    print(user_tg_id)
    for friend in friend_for_invite_to_event:
        print(friend[2], friend[3])
        friend_list_txt += f'ID: {friend[2]} Имя: {friend[3]}\n'
        markup.add(
            types.InlineKeyboardButton(f'ID: {friend[2]} | Имя: {friend[3]}\n',
                                       callback_data=f'{event_id}invite_friend_to_event{friend[2]}'))
    markup.add(
        types.InlineKeyboardButton(f'Отмена',
                                   callback_data=f'invite_friend_to_event_cancel'))

    print(friend_list_txt)
    if friend_list_txt == '':
        friend_list_txt = 'Список друзей пуст(\nДрузья могут отсылать вам заявки по ID'
        bot.send_message(message.chat.id, friend_list_txt)
    else:
        bot.send_message(message.chat.id, 'Загрузка друзей...', reply_markup=REMOVE_BUTTON_SETTING)
        bot.send_message(message.chat.id, 'Выберите друга, которого хотите пригласить:\n', reply_markup=markup)
    cur.close()
    conn.close()


def get_id_from_database(message):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.from_user.id
    print(user_tg_id)

    cur.execute(
        'select id from users where tg_id = %d' % (user_tg_id)
    )

    database_user_id = cur.fetchall()[0][0]

    cur.close()
    conn.close()

    return database_user_id


def get_tg_id_from_database(id):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'select tg_id from users where id = %d' % (id)
    )

    database_user_id = cur.fetchall()[0][0]

    cur.close()
    conn.close()

    return database_user_id


def add_friend(message, friend_info_id, status):
    user_id = get_id_from_database(message)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # if status == 'invite':
    #     status1 = 'rejected'
    # else:
    #     status1 = status

    cur.execute(
        'update friend_list set friend_status = "%s" where user_id = %d and friend_id = %d' % (
            status, user_id, friend_info_id)
    )

    conn.commit()

    cur.execute(
        'update friend_list set friend_status = "%s" where user_id = %d and friend_id = %d' % (
            status, friend_info_id, user_id)
    )

    conn.commit()

    cur.close()
    conn.close()
    if status == 'friend':
        bot.send_message(message.chat.id, 'Заявка в друзья успешно принята')
    elif status == 'rejected':
        bot.send_message(message.chat.id, 'Заявка в друзья отклонена')
    elif status == 'deleted':
        bot.send_message(message.chat.id, 'Пользователь удален из ваших друзей')
    # bot.send_message(message.chat.id, 'Заявку принята')
    create_profile_menu(message)


def on_click_menu_confirmation(message, friend_info_id):
    # bot.send_message(message.chat.id, 'Что-то сделали с другом')
    if message.text == 'Принять заявку':
        add_friend(message, friend_info_id, 'friend')
        # bot.send_message(message.chat.id, 'Заявка принята')
    elif message.text == 'Отклонить заявку':
        # bot.send_message(message.chat.id, 'Заявка отклонена')
        add_friend(message, friend_info_id, 'rejected')
    # elif message.text == 'Удалить из друзей':
    elif message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Отмена')
        create_profile_menu(message)
    elif message.text == 'Удалить пользователя из друзей':
        add_friend(message, friend_info_id, 'deleted')
    # print('test')


def get_friend_list(message):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.from_user.id

    cur.execute(
        'select distinct TBL2.name, user_id, friend_id, TBL1.name, friend_status from friend_list as TBL left join users as TBL1 on TBL.friend_id = TBL1.id left join users as TBL2 on TBL2.id = TBL.user_id where TBL2.tg_id = %d and friend_status = "friend"' % (
            user_tg_id)
    )

    friend_list = cur.fetchall()

    markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton('Тест', callback_data='delete'))

    friend_list_txt = ''

    for friend in friend_list:
        print(friend[2], friend[3])
        friend_list_txt += f'ID: {friend[2]} Имя: {friend[3]}\n'
        markup.add(types.InlineKeyboardButton(f'ID: {friend[2]} | Имя: {friend[3]}\n',
                                              callback_data=f'delete_menu{friend[2]}'))
        print(f'delete_menu{friend[2]}')

    if friend_list_txt == '':
        friend_list_txt = 'Ваш список друзей пуст(\nВы можете добавить друзей с помощью их ID'
        bot.send_message(message.chat.id, friend_list_txt)

    else:
        bot.send_message(message.chat.id, 'Ваш список друзей:', reply_markup=markup)
        # create_main_menu(message)
    print(friend_list)
    # bot.send_message(message.chat.id, friend_list_txt, reply_markup=markup)
    cur.close()
    conn.close()


def create_event_from_data(message, event_info):
    event_info_list = []
    creator_id = get_id_from_database(message)
    for info in event_info.values():
        event_info_list.append(info)
    event_info_list.append(creator_id)
    print(tuple(event_info_list))

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO event_list (name, time_and_date, place, info, creator_id, event_status) VALUES ('%s', '%s', '%s', '%s', '%d', 'active')" % tuple(
            event_info_list)
    )

    conn.commit()

    cur.close()
    conn.close()


def get_event_info_from_user(message, event_info):
    event_dop_info = message.text
    event_info['info'] = event_dop_info
    print(event_info)
    create_event_from_data(message, event_info)
    bot.send_message(message.chat.id,
                     f'Мероприятие {event_info["event_name"]} успешно создано\nВы можете найти его в списке ваших мероприятий')

    create_main_menu(message)
    # bot.register_next_step_handler(message, create_event_from_data, event_info=event_info)


def get_event_place_from_user(message, event_info):
    event_place = message.text
    event_info['place'] = event_place
    print(event_info)

    bot.send_message(message.chat.id, 'Введите дополнительную информацию о мероприятии:')
    bot.register_next_step_handler(message, get_event_info_from_user, event_info=event_info)


def get_event_time_and_date_from_user(message, event_info):
    event_date_and_time = message.text
    event_info['time_and_date'] = event_date_and_time
    print(event_info)
    bot.send_message(message.chat.id, 'Введите место проведения мероприятия:')
    bot.register_next_step_handler(message, get_event_place_from_user, event_info=event_info)


def get_event_name_from_user(message):
    event_name = message.text
    # creator_id = get_id_from_database(message)
    event_info = {
        'event_name': event_name
        # ,'creator_id': creator_id
    }
    print(event_info)

    bot.send_message(message.chat.id, 'Введите дату и время мероприятия в любом удобном для вас формате:')
    bot.register_next_step_handler(message, get_event_time_and_date_from_user, event_info=event_info)


def create_event(message):
    bot.send_message(message.chat.id, 'Создаём мероприятие', reply_markup=REMOVE_BUTTON_SETTING)
    bot.send_message(message.chat.id, 'Введите название мероприятия:')

    bot.register_next_step_handler(message, get_event_name_from_user)


def get_id_user_by_tg_ig(tg_id):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    cur.execute(
        'select id from users where tg_id = %d' % (tg_id)
    )

    database_user_id = cur.fetchall()[0][0]

    cur.close()
    conn.close()

    return database_user_id


def get_event_list_create_by_me_by_chat_id(message):
    bot.send_message(message.chat.id, 'Загрузка мероприятий...', reply_markup=REMOVE_BUTTON_SETTING)
    # bot.delete_message(message.chat.id, message.message_id - 1)

    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # user_id = get_id_from_database(message)
    # user_id = user
    user_id = get_id_user_by_tg_ig(message.chat.id)

    cur.execute(
        'select * from event_list where creator_id = %d' % (user_id)
    )

    event_list = cur.fetchall()

    friend_list = cur.fetchall()

    markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton('Тест', callback_data='delete'))

    friend_list_txt = ''
    print(event_list)
    for event in event_list:
        print(event[0], event[1])
        markup.add(
            types.InlineKeyboardButton(f'ID: {event[0]} | Имя: {event[1]}',
                                       callback_data=f'event_menu{event[0]}'))
    markup.add(types.InlineKeyboardButton('Отмена', callback_data='event_cancel_menu'))
    if event_list == []:
        friend_list_txt = 'Вы ещё не создали ни одного мероприятия(\n'
        bot.send_message(message.chat.id, friend_list_txt)
        create_event_type_menu(message)
    else:
        bot.send_message(message.chat.id, 'Ваш список мероприятий:', reply_markup=markup)
    # print(friend_list)

    cur.close()
    conn.close()


def create_event_type_menu(message):
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Мероприятия созданные мной')
    btn2 = types.KeyboardButton('Мероприятия в которых я участвую')
    btn3 = types.KeyboardButton('Назад')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)

    bot.send_message(message.chat.id, 'Выберите тип мероприятия', reply_markup=markup)
    bot.register_next_step_handler(message, on_click_events_type)


def on_click_main_menu(message):
    if message.text == 'Профиль':
        # bot.send_message(message.chat.id, 'Профиль')
        profile_menu(message)
        create_profile_menu(message)
    elif message.text == 'Заявки в друзья':
        get_friend_invite(message)
        # dgsgs
        # create_main_menu(message)
    elif message.text == 'Создать мероприятие':
        create_event(message)
    elif message.text == 'Мои мероприятия':
        create_event_type_menu(message)
    else:
        bot.reply_to(message, f'Неизвестная команда: {message.text}')
        create_main_menu(message)


def on_click_events_type(message):
    if message.text == 'Мероприятия созданные мной':
        get_event_list_create_by_me_by_chat_id(message)
    elif message.text == 'Мероприятия в которых я участвую':
        pass
    elif message.text == 'Назад':
        create_main_menu(message)
        # print(False)


def profile_menu(message):
    # create_table()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.from_user.id
    # print(user_tg_id)
    cur.execute(
        f'select * from users where tg_id = {user_tg_id}'
    )
    # print(cur)
    user_info = cur.fetchall()

    user_info_txt = ''
    # print(user_info)
    for info in user_info:
        user_info_txt += f'Ваш профиль:\nID для друзей: {info[0]}\nИмя: {info[1]}'
    bot.send_message(message.chat.id, user_info_txt)
    cur.close()
    conn.close()


def check_user(message):
    # print('Работает функция проверки')
    # create_table()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    user_tg_id = message.from_user.id

    cur.execute(
        'select count(*) from users where tg_id = %d' % (user_tg_id)
    )
    # conn.commit()
    # возвращает все найденные записи
    count_accounts = cur.fetchall()
    #
    # print('Количество аккаунтов пользователя: ', count_accounts[0])

    cur.close()
    conn.close()
    if list(count_accounts[0])[0] > 0:
        return True
    else:
        return False


def check_user_name(message):
    name = message.text.strip()

    if '|' not in name:
        create_user(message)
    else:
        bot.send_message(message.chat.id, 'Запрещённый символ | в вашем имени, давайте попробуем ещё раз')
        start_bot(message)


# Кнопка при старт в самом боте
@bot.message_handler(commands=['start'])
def start_bot(message):
    create_table()
    user_in_database = check_user(message)
    print(message.chat.id)
    if user_in_database is False:
        bot.send_message(message.chat.id, 'Привет!')
        bot.send_message(message.chat.id, 'Введи своё имя, чтоб твои друзья могли тебя узнать:')
        bot.register_next_step_handler(message, check_user_name)
    else:
        create_main_menu(message)


if __name__ == '__main__':
    print('start bot')
    bot.polling(none_stop=True)
