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


def connect_db(dbname):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    return conn, cur


def close_connect_to_db(conn, cur):
    cur.close()
    conn.close()


def create_table():
    print('Функция создания БД')
    conn, cur = connect_db(DBNAME)

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(10), tg_id int, username varchar(50))'
    )
    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS friend_list (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id int, friend_id int, friend_status varchar(20))'
    )
    conn.commit()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS event_list (id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(100), time_and_date varchar(50), place varchar(100), info varchar(511), creator_id int)'
    )
    conn.commit()

    close_connect_to_db(conn, cur)


def find_user_in_db(message):
    conn, cur = connect_db(DBNAME)

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


def create_main_menu(message):
    print('Создал меню')
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Создать мероприятие')
    btn2 = types.KeyboardButton('Мои мероприятия')
    markup.row(btn1)
    markup.row(btn2)
    btn3 = types.KeyboardButton('Профиль')
    btn4 = types.KeyboardButton('Заявки в друзья')
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


def check_user_name(message):
    name = message.text.strip()

    prohibited_symbols = ['|', '/']

    for symbol in prohibited_symbols:
        if symbol in name:
            bot.send_message(message.chat.id, 'Запрещённый символ | в вашем имени, давайте попробуем ещё раз')
            start_bot(message)
            break
    else:
        # pass
        create_user(message)
        create_main_menu(message)


def create_user(message):
    print('Работает функция создания пользователя')
    conn, cur = connect_db(DBNAME)

    name = message.text.strip()

    tg_id = message.from_user.id
    username = str(message.from_user.username).strip()

    cur.execute(
        "INSERT INTO users (name, tg_id, username) VALUES ('%s', '%d', '%s')" % (name, tg_id, username)
    )
    conn.commit()

    cur.execute(
        'select * from users'
    )
    # возвращает все найденные записи
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Имя {el[0]}\n'
        print(el[0], el[1])
        print(el)

    print(list(users))
    bot.send_message(message.chat.id,
                     f'Теперь ваши друзья будут видеть вас под именем: {name}.\n\nЭто имя можно будет изменить в будущем')

    close_connect_to_db(conn, cur)

    # create_main_menu(message)


# Кнопка при старт в самом боте
@bot.message_handler(commands=['start'])
def start_bot(message):
    create_table()
    user_in_database = find_user_in_db(message)
    if user_in_database is False:
        bot.send_message(message.chat.id, 'Привет!')
        bot.send_message(message.chat.id, 'Введи своё имя, чтоб твои друзья могли тебя узнать:')

        bot.register_next_step_handler(message, check_user_name)

    else:
        create_main_menu(message)
        # bot.register_next_step_handler(message, on_click_main_menu)


if __name__ == '__main__':
    print('start bot')
    bot.polling(none_stop=True)
