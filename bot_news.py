import telebot
import sqlite3 as lite
from typing import List, Any
from newsapi import NewsApiClient
import config

list_hello = ("Привет", "Здравствуй", "Hello","ghbdtn","Ghbdtn")
#
bot = telebot.TeleBot("", parse_mode=None)
#
conn = lite.connect('mybase.db', check_same_thread=False)
c = conn.cursor()
    # Создать таблицу
state = 0
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY,'
            ' f_name varchar(50), l_name varchar(50));')
c.execute('CREATE TABLE IF NOT EXISTS categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'cat_name varchar(100), user_id INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS keywords (keyword_id integer primary key AUTOINCREMENT,'
            'word_name varchar(100), user_id INTEGER)')
data = c.fetchone()
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('Add news category', 'Add news keyword')
keyboard.row('Show my categories', 'Show my keywords')
keyboard.row('Remove category', 'Remove keyword')
api = NewsApiClient(api_key='')
"""#@bot.message_handler(commands=['start', 'help'])
#def handle_start_help(message):
#    bot.reply_to(message, "Желаешь получить новости?")

#
@bot.message_handler(func=lambda message: True)
def answer_to_message(message):
    print(message.from_user.id)
    if message.text in list_hello:
        bot.send_message(message.from_user.id, "И тебе привет!")"""
def add_category(message):
    cat_data = c.execute(f"SELECT * FROM categories WHERE cat_name = '{message.text}' "
                           f"AND user_id = {message.from_user.id}").fetchone()
    print(cat_data)
    if cat_data is None:
        c.execute(f"INSERT INTO categories (cat_name, user_id) VALUES "
                    f" ('{message.text}',"
                    f" {message.from_user.id})")
        conn.commit()
        #conn.close()
    else:
        bot.reply_to(message, "This category is already exists")


def add_keyword(message):
    key_data = c.execute(f"SELECT * FROM keywords WHERE word_name = '{message.text}' "
                           f"AND user_id = {message.from_user.id}").fetchone()
    if key_data is None:
        c.execute(f"INSERT INTO keywords (word_name, user_id) VALUES "
                    f" ('{message.text}',"
                    f" {message.from_user.id})")
        conn.commit()
    else:
        bot.reply_to(message, "This keyword is already exists")


def show_categories(message):
    user_cats = c.execute(f"SELECT cat_name FROM categories WHERE user_id = {message.from_user.id}").fetchall()
    if user_cats is None:
        bot.reply_to(message, "You haven't any categories")
    else:
        bot.reply_to(message, f"List of your chosen categories {user_cats}")


def show_keywords(message):
    user_keyw = c.execute(f"SELECT word_name FROM keywords WHERE user_id = {message.from_user.id}").fetchall()
    if user_keyw is None:
        bot.reply_to(message, "You haven't any keywords")
    else:
        bot.reply_to(message, f"List of your chosen categories : {user_keyw}")
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data = c.execute(f"SELECT * FROM users WHERE user_id = {message.from_user.id}").fetchone()
    if user_data is None:
        c.execute(f"INSERT INTO users (user_id, f_name, l_name) VALUES "
                    f" ({message.from_user.id},"
                    f" '{message.from_user.first_name}',"
                    f" '{message.from_user.last_name}')")
        conn.commit()
        conn.close()
    bot.reply_to(message, f"Привет, {message.from_user.first_name}, рады знакомству!\n Выбирай!",
                 reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, f"msg = {message.text} There is a short list of possible commands\n"
                          f"/start - this command registry user (if he isn't registry) and opens main menu\n"
                          f"/show_news - this command show news based on chosen categories and keywords\n")


@bot.message_handler(commands=['show_news'])
def get_news(message):
    bot.reply_to(message, "Новости : \n")
    newsapi = NewsApiClient(api_key='')
    user_cats: List[Any] = c.execute(
        f"SELECT cat_name FROM categories WHERE user_id = {message.from_user.id}").fetchall()
    user_keyw: List[Any] = c.execute(
        f"SELECT word_name FROM keywords WHERE user_id = {message.from_user.id}").fetchall()

    category_list = [item for t in user_cats for item in t]
    keyword_list = [item for t in user_keyw for item in t]

    for cat in category_list:
        for keyword in keyword_list:
            top_headlines = newsapi.get_top_headlines(q=keyword,
                                                      category=cat,
                                                      page_size=10,
                                                      page=1)
            bot.reply_to(message, f"News category is \"{cat}\"\n News keyword is \"{keyword}\"\n")

            if top_headlines['totalResults']:
                if top_headlines['totalResults'] > 10:
                    cnt = 10
                else:
                    cnt = top_headlines['totalResults']
                for i in range(cnt):

                    bot.reply_to(message, f"====== {i+1} Article =========\n")
                    bot.reply_to(message, f" Title \n {top_headlines['articles'][i]['title']}\n"
                                          f" Link {top_headlines['articles'][i]['url']}\n")
            else:
                bot.reply_to(message, "Can't found any news!\n")


@bot.message_handler(content_types=["text"])
def main(message):
    global state

    if state == 1:
        print(message.text)
        add_category(message)
        state = 0
    elif state == 2:
        add_keyword(message)
        state = 0

    bot.send_message(message.chat.id, 'done', reply_markup=telebot.types.ReplyKeyboardRemove())
    if message.text == "Add news category":
        state = 1
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        keyboard1.row('sports', 'business')
        keyboard1.row('entertainment', 'general')
        keyboard1.row('health', 'science')
        keyboard1.row('technology')
        bot.send_message(message.chat.id, "Choose the possible categories", reply_markup=keyboard1)
    elif message.text == 'Add news keyword':
        state = 2
        bot.send_message(message.chat.id, "Enter new keyword")
    elif message.text == 'Show my categories':
        show_categories(message)
    elif message.text == 'Show my keywords':
        show_keywords(message)
    elif message.text == 'Remove category':
        state = 5
        bot.send_message(message.chat.id, "Enter name of category what you want to delete")
    elif message.text == 'Remove keyword':
        state = 6
        bot.send_message(message.chat.id, "Enter name of keyword what you want to delete")


bot.polling()