''' Персонализированный бот для девушки:
необходимо будет добавить id девушки, чтобы только она могла туда писать
для заполнения списка желаний (сделаю условный оператор в start) '''

import telebot
from telebot import types
import sqlite3
from datetime import datetime

token = '6247864968:AAHlRTVqb20mXsm9S4QKYqNGqq-XibetJsw'
bot = telebot.TeleBot(token)

name_dream = None
prise = None


@bot.message_handler(commands=['start'])
def start(message):
    db = sqlite3.connect('Dream.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS dreams(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR,
        prise DECIMAL,
        period VARCHAR,
        data DATE
    )""")
    db.commit()
    cursor.close()
    db.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Готова', callback_data='Ready'))
    bot.send_message(message.chat.id,
                     'Привет, Любимая! Я <b>исполнитель твох мечтаний</b> 🥰 Здесь ты можешь написать, чего ты желаешь получить в короткий или долгосрочный период. Я буду отслеживать твои желания и по возможности исполнять их, <b>не стесняйся писать</b>, чего ты хочешь получить!',
                     reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'Ready':
        bot.send_message(call.message.chat.id,
                         'Напиши <b>название</b> того, чего хочешь получить. Можешь расписать подробно, чтобы было более точно и понятно 😋',
                         parse_mode='html')
    elif call.data == 'Continue':
        bot.send_message(call.message.chat.id,
                         'Напиши <b>название</b> того, чего хочешь получить. Можешь расписать подробно, чтобы было более точно и понятно 😋',
                         parse_mode='html')
    elif call.data == 'Basket':
        db = sqlite3.connect('Dream.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM dreams")
        list_dreams = cursor.fetchall()
        s = ''
        if len(list_dreams) != 0:
            for i in list_dreams:
                s += f'{i[0]}) {i[1]} - {i[2]} - {i[3]}\n'
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='Continue'))
            markup.add(types.InlineKeyboardButton('Выполнено', callback_data='Delete'))
            bot.send_message(call.message.chat.id, s, reply_markup=markup)
        else:
            s = '<b>Список желаний пуст</b>'
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='Continue'))
            bot.send_message(call.message.chat.id, s, reply_markup=markup, parse_mode='html')
        cursor.close()
        db.close()
    elif call.data == "Delete":
        bot.send_message(call.message.chat.id, 'Напиши <b>цифру</b>, под которой желание исполнилось 👇',
                         parse_mode='html')
        bot.register_next_step_handler(call.message, set_digit)


@bot.message_handler(content_types=['text'])
def name(message):
    global name_dream
    name_dream = message.text
    db = sqlite3.connect('Dream.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO dreams(name) VALUES('{name_dream}')")
    db.commit()
    cursor.close()
    db.close()
    bot.send_message(message.chat.id, 'Напиши <b>стоимость</b> выбранной вещи или услуги💰', parse_mode='html')
    bot.register_next_step_handler(message, set_period)


def set_period(message):
    global prise
    prise = message.text
    db = sqlite3.connect('Dream.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE dreams SET prise = '{prise}' WHERE name = '{name_dream}'")
    db.commit()
    cursor.close()
    db.close()
    bot.send_message(message.chat.id,
                     'Напиши <b>период</b>, в течение которого хочешь получить выбранную вещь или услугу ⏳',
                     parse_mode='html')
    bot.register_next_step_handler(message, get_period)


def get_period(message):
    period = message.text
    db = sqlite3.connect('Dream.db')
    cursor = db.cursor()
    cursor.execute(f"UPDATE dreams SET period = '{period}' WHERE name = '{name_dream}'")
    db.commit()
    cursor.execute(f"UPDATE dreams SET data = '{datetime.now()}' WHERE name = '{name_dream}'")
    db.commit()
    cursor.close()
    db.close()
    markup = types.InlineKeyboardMarkup()
    bt_1 = types.InlineKeyboardButton(text='Продолжить', callback_data='Continue')
    markup.add(bt_1)
    bt_2 = types.InlineKeyboardButton(text='Список желаний', callback_data='Basket')
    markup.add(bt_2)
    bot.send_message(message.chat.id,
                     f'Супер! Мечта принята! 🤩 <b>Желания</b>: {name_dream}\nСтоимость: {prise}\nПериод: {period}\nВозвращайся с новыми желаниями 😍',
                     reply_markup=markup, parse_mode='html')


def set_digit(message):
    digit = message.text
    db = sqlite3.connect('Dream.db')
    cursor = db.cursor()
    cursor.execute(f"SELECT name FROM dreams WHERE id = '{digit}'")
    f = cursor.fetchone()
    cursor.execute(f"DELETE FROM dreams WHERE id = '{digit}'")
    db.commit()
    cursor.execute(f"UPDATE dreams Set id = id - 1 WHERE id > '{digit}'")
    db.commit()
    cursor.execute("UPDATE SQLITE_SEQUENCE SET seq = 0")
    db.commit()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Продолжить', callback_data='Continue'))
    markup.add(types.InlineKeyboardButton(text='Список желаний', callback_data='Basket'))
    bot.send_message(message.chat.id, f'Мечта - <b>{f[0]}</b> - исполнена ✅', reply_markup=markup, parse_mode='html')


bot.infinity_polling()
