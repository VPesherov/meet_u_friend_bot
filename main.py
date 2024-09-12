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


def connect_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    return conn, cur


def close_connect_to_db(conn, cur):
    cur.close()
    conn.close()


def create_table():
    print('Функция создания БД')
    conn, cur = connect_db()

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

    close_connect_to_db(conn, cur)


def find_user_in_db(message):
    conn, cur = connect_db()

    user_tg_id = message.from_user.id

    cur.execute(
        'select count(*) from users where tg_id = %d' % (user_tg_id)
    )
    # возвращает все найденные записи
    count_accounts = cur.fetchall()

    close_connect_to_db(conn, cur)

    if list(count_accounts[0])[0] > 0:
        return True
    else:
        return False


def create_main_menu(message, user_info_dict):
    print('Создал меню')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Создать мероприятие')
    btn2 = types.KeyboardButton('Мои мероприятия')
    markup.row(btn1)
    markup.row(btn2)
    btn3 = types.KeyboardButton('Профиль')
    btn4 = types.KeyboardButton('Приглашения')
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    bot.register_next_step_handler(message, on_click_main_menu, user_info_dict)


def check_user_name(message):
    name = message.text.strip()

    prohibited_symbols = ['|', '/']

    for symbol in prohibited_symbols:
        if symbol in name:
            bot.send_message(message.chat.id, 'Запрещённый символ | в вашем имени, давайте попробуем ещё раз')
            start_bot(message)
            break
    else:
        create_user(message)


def get_user_info_by_tg_id(tg_id):
    conn, cur = connect_db()

    user_info_dict = {
        'id': '',
        'name': '',
        'tg_id': '',
        'username': '',
        'chat_id': ''
    }

    cur.execute(
        'select id, name, tg_id, username, chat_id from users where tg_id = %d' % (tg_id)
    )

    user_info = cur.fetchall()
    print(user_info[0])

    for number, key in enumerate(user_info_dict):
        user_info_dict[key] = user_info[0][number]

    print(user_info_dict)
    close_connect_to_db(conn, cur)

    return user_info_dict


def get_user_info_by_id(id):
    conn, cur = connect_db()

    user_info_dict = {
        'id': '',
        'name': '',
        'tg_id': '',
        'username': '',
        'chat_id': ''
    }

    cur.execute(
        'select id, name, tg_id, username, chat_id from users where id = %d' % (id)
    )

    user_info = cur.fetchall()
    if not user_info:
        return False
    print(user_info[0])

    for number, key in enumerate(user_info_dict):
        user_info_dict[key] = user_info[0][number]

    print(user_info_dict)
    close_connect_to_db(conn, cur)

    return user_info_dict


def create_user(message):
    print('Работает функция создания пользвоателя')
    conn, cur = connect_db()

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

    bot.send_message(message.chat.id,
                     f'Теперь ваши друзья будут видеть вас под именем: {name}.\n\nЭто имя можно будет изменить в будущем')
    close_connect_to_db(conn, cur)

    user_info_dict = get_user_info_by_tg_id(tg_id)
    create_main_menu(message, user_info_dict)


def get_profile(message):
    # create_table()
    conn, cur = connect_db()

    user_tg_id = message.from_user.id
    cur.execute(
        f'select * from users where tg_id = {user_tg_id}'
    )
    user_info = cur.fetchall()

    user_info_txt = ''
    for info in user_info:
        user_info_txt += f'Ваш профиль:\nID для друзей: {info[0]}\nИмя: {info[1]}'
    bot.send_message(message.chat.id, user_info_txt)

    close_connect_to_db(conn, cur)


def create_profile_menu(message, user_info_dict):
    print('Создал меню профиля')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
    bot.register_next_step_handler(message, on_click_profile_menu, user_info_dict)


def get_friend_invite(message, user_info_dict):
    conn, cur = connect_db()

    user_tg_id = int(user_info_dict['tg_id'])

    cur.execute(
        'select distinct TBL2.name, user_id, friend_id, TBL1.name, friend_status from friend_list as TBL left join users as TBL1 on TBL.friend_id = TBL1.id left join users as TBL2 on TBL2.id = TBL.user_id where TBL2.tg_id = %d and friend_status = "invite"' % (
            user_tg_id)
    )

    friend_list = cur.fetchall()

    markup = types.InlineKeyboardMarkup()

    friend_list_txt = ''

    for friend in friend_list:
        friend_list_txt += f'ID: {friend[2]} Имя: {friend[3]}\n'
        markup.add(
            types.InlineKeyboardButton(f'ID: {friend[2]} | Имя: {friend[3]}\n',
                                       callback_data=f'{user_tg_id}add_new_friend_menu{friend[2]}'))

    if friend_list_txt == '':
        friend_list_txt = 'Список заявок пуст(\nДрузья могут отсылать вам заявки по ID'
        bot.send_message(message.chat.id, friend_list_txt)
        create_profile_menu(message, user_info_dict)
    else:
        bot.send_message(message.chat.id, 'С вами хотят подружиться:\n', reply_markup=markup)
        bot.register_next_step_handler(message, on_click_profile_menu, user_info_dict)
    close_connect_to_db(conn, cur)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if 'add_new_friend_menu' in callback.data:
        user_tg_id, number_add = str(callback.data).replace('add_new_friend_menu', '|').strip().split('|')
        if callback.data == user_tg_id + 'add_new_friend_menu' + number_add:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

            friend_info_id = int(number_add)

            friend_info_dict = get_user_info_by_id(friend_info_id)

            invite_text = f'Выбран друг:\nID: {friend_info_dict["id"]} Имя: {friend_info_dict["name"]} \nДобавить в друзья?'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

            btn1 = types.KeyboardButton('Принять заявку')
            btn2 = types.KeyboardButton('Отклонить заявку')
            btn3 = types.KeyboardButton('Отмена')

            markup.row(btn1)
            markup.row(btn2)
            markup.row(btn3)

            user_info_dict = get_user_info_by_tg_id(int(user_tg_id))

            bot.send_message(callback.message.chat.id, invite_text, reply_markup=markup)
            bot.register_next_step_handler(callback.message, on_click_menu_confirmation,
                                           friend_info_dict=friend_info_dict, user_info_dict=user_info_dict)
    if 'delete_friend_menu' in callback.data:
        user_tg_id, number_delete = str(callback.data).replace('delete_friend_menu', '|').strip().split('|')
        if callback.data == user_tg_id + 'delete_friend_menu' + number_delete:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Да')
            btn2 = types.KeyboardButton('Отмена')
            markup.row(btn1)
            markup.row(btn2)
            friend_info_id = int(number_delete)
            friend_info = get_user_info_by_id(friend_info_id)
            user_info_dict = get_user_info_by_tg_id(int(user_tg_id))

            invite_text = f'Выбран друг:\n{friend_info_id} | {friend_info["name"]} \n Вы действительно хотите удалить его?'
            bot.send_message(callback.message.chat.id, invite_text, reply_markup=markup)
            bot.register_next_step_handler(callback.message, on_click_menu_delete_confirmation,
                                           friend_info_id=friend_info_id, user_info_dict=user_info_dict)



def on_click_menu_delete_confirmation(message, friend_info_id, user_info_dict):
    if message.text == 'Да':
        change_friend_status(friend_info_id, 'deleted', user_info_dict)
        bot.send_message(message.chat.id, 'Пользователь удален из ваших друзей')
    elif message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Отмена')
    create_profile_menu(message, user_info_dict)


def change_friend_status(friend_info_id, status, user_info_dict):
    user_id = int(user_info_dict['id'])

    conn, cur = connect_db()

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
    close_connect_to_db(conn, cur)


def on_click_menu_confirmation(message, friend_info_dict, user_info_dict):
    if message.text == 'Принять заявку':
        # pass
        # add_friend(message, friend_info_id, 'friend')
        change_friend_status(friend_info_dict['id'], 'friend', user_info_dict)
        bot.send_message(message.chat.id, 'Заявка в друзья успешно принята')
        create_profile_menu(message, user_info_dict)
    elif message.text == 'Отклонить заявку':
        change_friend_status(friend_info_dict['id'], 'rejected', user_info_dict)
        bot.send_message(message.chat.id, 'Заявка в друзья отклонена')
        create_profile_menu(message, user_info_dict)
    elif message.text == 'Отмена':
        bot.send_message(message.chat.id, 'Отмена')
        create_profile_menu(message, user_info_dict)
    elif message.text == 'Удалить пользователя из друзей':
        # pass
        bot.send_message(message.chat.id, 'Пользователь удален из ваших друзей')
        # add_friend(message, friend_info_id, 'deleted')


def check_friend(my_id, invite_friend_id):
    conn, cur = connect_db()

    cur.execute(
        'select id from friend_list where user_id = %d and friend_id = %d' % (invite_friend_id, my_id)
    )
    friend_status = cur.fetchall()
    print(friend_status)
    close_connect_to_db(conn, cur)

    if not friend_status:
        return False
    else:
        return True


def return_friend_status(my_id, invite_friend_id, status):
    conn, cur = connect_db()

    cur.execute(
        'select id from friend_list where user_id = %d and friend_id = %d and friend_status = "%s"' % (
            invite_friend_id, my_id, status)
    )
    friend_status = cur.fetchall()
    print('status')
    print(friend_status)
    close_connect_to_db(conn, cur)

    if not friend_status:
        return False
    else:
        return True


def send_friend_invitation(message, user_info_dict):
    invite_friend_id = message.text
    try:
        invite_friend_id = int(invite_friend_id)
    except:
        print('Ошибка:\n', traceback.format_exc())
        bot.send_message(message.chat.id, 'Ошибка\nID друга - должно быть числом')
        create_profile_menu(message, user_info_dict)
        return 0

    my_id = user_info_dict['id']

    if my_id == invite_friend_id:
        bot.send_message(message.chat.id, 'Вы не можете отправить заявку самому себе')
        create_profile_menu(message, user_info_dict)
        return 0

    print(user_info_dict['id'], invite_friend_id)
    conn, cur = connect_db()

    if get_user_info_by_id(invite_friend_id) is False:
        close_connect_to_db(conn, cur)
        bot.send_message(message.chat.id, 'Пользователь с данным ID не найден')
        create_profile_menu(message, user_info_dict)
        return 0

    friend_status = check_friend(my_id, invite_friend_id)
    my_status = check_friend(invite_friend_id, my_id)

    my_friend_status = return_friend_status(my_id, invite_friend_id, "friend")
    friend_friend_status = return_friend_status(invite_friend_id, my_id, "friend")
    print(my_friend_status, friend_friend_status)
    if my_friend_status == friend_friend_status == True:
        bot.send_message(message.chat.id, 'Данный пользователь уже есть у вас в друзьях')
        create_profile_menu(message, user_info_dict)
        return 0
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

    conn.commit()

    close_connect_to_db(conn, cur)

    bot.send_message(message.chat.id, 'Заявка в друзья отправлена')
    create_profile_menu(message, user_info_dict)


def on_click_profile_menu(message, user_info_dict):
    if message.text == 'Назад в меню':
        create_main_menu(message, user_info_dict)
    if message.text == 'Список друзей':
        get_friend_list(message, user_info_dict)
        bot.register_next_step_handler(message, on_click_profile_menu, user_info_dict)
    if message.text == 'Заявки в друзья':
        get_friend_invite(message, user_info_dict)
        # create_profile_menu(message, user_info_dict)
    if message.text == 'Добавить в друзья':
        bot.send_message(message.chat.id, 'Попросите вашего друга сообщить ID\nВведите ID друга:')
        bot.register_next_step_handler(message, send_friend_invitation, user_info_dict)
    if message.text == 'Удалить из друзей':
        bot.send_message(message.chat.id, 'Выберите друга, которого хотите удалить')
        get_friend_list(message, user_info_dict)
        bot.register_next_step_handler(message, on_click_profile_menu, user_info_dict)


def get_friend_list(message, user_info_dict):
    conn, cur = connect_db()

    user_tg_id = int(user_info_dict['tg_id'])

    cur.execute(
        'select distinct TBL2.name, user_id, friend_id, TBL1.name, friend_status from friend_list as TBL left join users as TBL1 on TBL.friend_id = TBL1.id left join users as TBL2 on TBL2.id = TBL.user_id where TBL2.tg_id = %d and friend_status = "friend"' % (
            user_tg_id)
    )

    friend_list = cur.fetchall()

    markup = types.InlineKeyboardMarkup()

    friend_list_txt = ''

    for friend in friend_list:
        print(friend[2], friend[3])
        friend_list_txt += f'ID: {friend[2]} Имя: {friend[3]}\n'
        markup.add(types.InlineKeyboardButton(f'ID: {friend[2]} | Имя: {friend[3]}\n',
                                              callback_data=f'{user_tg_id}delete_friend_menu{friend[2]}'))
        print(f'delete_menu{friend[2]}')

    if friend_list_txt == '':
        friend_list_txt = 'Ваш список друзей пуст(\nВы можете добавить друзей с помощью их ID'
        bot.send_message(message.chat.id, friend_list_txt)

    else:
        bot.send_message(message.chat.id, 'Ваш список друзей:', reply_markup=markup)

    close_connect_to_db(conn, cur)


def create_event_from_data(event_info, user_info_dict):
    event_info_list = []
    creator_id = user_info_dict['id']
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


def get_event_info_from_user(message, event_info, user_info_dict):
    event_dop_info = message.text
    if event_dop_info == 'Отмена':
        create_main_menu(message, user_info_dict)
        return 0
    event_info['info'] = event_dop_info
    print(event_info)
    create_event_from_data(event_info, user_info_dict)
    bot.send_message(message.chat.id,
                     f'Мероприятие:\n{event_info["event_name"]}\nуспешно создано!\nВы можете найти его в списке ваших мероприятий')
    create_main_menu(message, user_info_dict)


def get_event_place_from_user(message, event_info, user_info_dict):
    event_place = message.text
    if event_place == 'Отмена':
        create_main_menu(message, user_info_dict)
        return 0
    event_info['place'] = event_place
    print(event_info)

    bot.send_message(message.chat.id, 'Введите дополнительную информацию о мероприятии:')
    bot.register_next_step_handler(message, get_event_info_from_user, event_info=event_info,
                                   user_info_dict=user_info_dict)


def get_event_time_and_date_from_user(message, event_info, user_info_dict):
    event_date_and_time = message.text
    if event_date_and_time == 'Отмена':
        create_main_menu(message, user_info_dict)
        return 0
    event_info['time_and_date'] = event_date_and_time
    print(event_info)
    bot.send_message(message.chat.id, 'Введите место проведения мероприятия:')
    bot.register_next_step_handler(message, get_event_place_from_user, event_info=event_info,
                                   user_info_dict=user_info_dict)


def get_event_name_from_user(message, user_info_dict):
    event_name = message.text
    if event_name == 'Отмена':
        create_main_menu(message, user_info_dict)
        return 0
    # creator_id = get_id_from_database(message)
    event_info = {
        'event_name': event_name
        # ,'creator_id': creator_id
    }
    print(event_info)

    bot.send_message(message.chat.id, 'Введите дату и время мероприятия в любом удобном для вас формате:')
    bot.register_next_step_handler(message, get_event_time_and_date_from_user, event_info=event_info,
                                   user_info_dict=user_info_dict)


def create_event(message, user_info_dict):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Отмена")
    bot.send_message(message.chat.id, 'Создаём мероприятие', reply_markup=REMOVE_BUTTON_SETTING)
    bot.send_message(message.chat.id, 'Введите название мероприятия:', reply_markup=markup)

    bot.register_next_step_handler(message, get_event_name_from_user, user_info_dict=user_info_dict)


def on_click_main_menu(message, user_info_dict):
    if message.text == 'Профиль':
        # print(get_user_info_by_id(30))
        get_profile(message)
        # get_user_info_by_tg_id(message.from_user.id)
        create_profile_menu(message, user_info_dict)
        # pass
    elif message.text == 'Приглашения':
        # get_friend_invite(message)
        pass
    elif message.text == 'Создать мероприятие':
        # pass
        create_event(message, user_info_dict)
        # create_main_menu(message, user_info_dict)
    elif message.text == 'Мои мероприятия':
        pass
        # create_event_type_menu(message)
    else:
        bot.reply_to(message, f'Неизвестная команда: {message.text}')
        create_main_menu(message, user_info_dict)


# Кнопка при старт в самом боте
@bot.message_handler(commands=['start'])
def start_bot(message):
    create_table()
    user_in_database = find_user_in_db(message)
    if user_in_database is False:
        bot.send_message(message.chat.id, 'Привет!')
        bot.send_message(message.chat.id, 'Введи своё имя, чтоб твои друзья могли тебя узнать:')

        bot.register_next_step_handler(message, check_user_name)
        # create_main_menu(message)
    else:
        user_info_dict = get_user_info_by_tg_id(message.chat.id)
        create_main_menu(message, user_info_dict)
        # bot.register_next_step_handler(message, on_click_main_menu)


if __name__ == '__main__':
    print('start bot')
    bot.polling(none_stop=True)
