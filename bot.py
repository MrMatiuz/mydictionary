import telebot
from telebot import types

import time
from openpyxl import load_workbook

from not_public import config
import global_var
import utils

import App

TOKEN = config.token

bot = telebot.TeleBot(TOKEN)

def reset_training_process_global_vars():
    global_var.answer = None
    global_var.start = None
    global_var.end = None
    global_var.start_training_flag = None
    global_var.app = None
    global_var.word_indxs = None

    global_var.i = 0
    global_var.__continue__ = None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global_var.status = 'start'
    modes = ['Training', 'Add new word', 'Correct existing word']
    markup = utils.generate_markup(modes)
    bot.send_message(
        message.chat.id
        ,f"Hello! What do you want to do?"
        ,reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def start_training(message):
    print(global_var.status)

    if global_var.status == 'start':
        if message.text == 'Training':
            training(message, bot)
        elif message.text == 'Add new word':
            add_new_word(message, bot)
        elif message.text == 'Correct existing word':
            bot.send_message(
                message.chat.id,
                f"Ups, I can't do it yet"
            )
    elif global_var.status == 'training_vocabulary':
        training_vocabulary(message, bot)
    # elif global_var.status == 'checking_word':
    #     print('============================================================')


def bot_asks_about_trainslation(message, bot, indx, word, translation):
    markup = utils.generate_markup()
    message = bot.send_message(
        message.chat.id
        ,f"Do you know word '{translation}'?"
        ,reply_markup=markup
        # ,reply_markup=types.ForceReply(selective=False)
    )
    global_var.start = time.time()
    bot.register_next_step_handler(message, client_answers_about_translation, bot, indx, word, translation)

def client_answers_about_translation(message, bot, indx, word, translation):
    answer = message.text
    print(answer)
    if answer in utils.base_answers.keys():
        if answer == 'Back home':
            app = global_var.app
            print("saving logs")
            app.write_user_activities_logs(app.client_activities, app.logs_table_name, app.dbname)
            reset_training_process_global_vars()
            go_home(message)
        else:
            # message = bot.send_message(
            #     message.chat.id
            #     ,utils.base_answers[message.text]
            # )
            message = bot.send_message(
                message.chat.id
                ,f"Correct word is '{word}'"
            )
            
            global_var.start_training_flag = False
            global_var.i += 1
            global_var.__continue__, global_var.answer, global_var.end = True, int(utils.true_false_answer[answer]), time.time()
            global_var.elapsed_time = global_var.end - global_var.start
            global_var.__if_client_answered__ = True
            
            time.sleep(1.5)
            training_process(message, bot)


def chat_func(message, bot, indx, word, translation):
    bot_asks_about_trainslation(message, bot, indx, word, translation)


def training_process(message, bot, random=False, inverse=False, chat_func=chat_func):
    app = global_var.app
    if global_var.start_training_flag:
        global_var.word_indxs = app.get_indxs(random)

    indx = global_var.word_indxs[global_var.i]
    activity = app.check_word(message=message, bot=bot, indx=indx, inverse=inverse, chat_func=chat_func)

    if global_var.__if_client_answered__ == True:

        activity['Success'] = str(global_var.answer)
        activity['Elapsed_time'] = str(global_var.elapsed_time)

        app.client_activities += [activity]
        global_var.__if_client_answered__ = False

        if global_var.i == app.batch_size - 1:
            print("saving logs")
            app.write_user_activities_logs(app.client_activities, app.logs_table_name, app.dbname)
            app.client_activities = []

            global_var.word_indxs = app.get_indxs(random)
            i = 0


def training_vocabulary(message, bot):
    global_var.status = 'training_vocabulary'
    print(global_var.status)
    # ================================================================================================
    app = App.App()
    app.read_vocabulary(app.dict_table_name, app.dbname)
    # ================================================================================================
    global_var.start_training_flag = True
    global_var.app = app
    training_process(chat_func=chat_func, message=message, bot=bot, random=True)
    # chat_func(message, bot, indx=1, word='qwe', translation='trans')
    # go_home(message)


def training_writing():
    print("I can't start writing training yet!")


def go_home(message, bot=bot):
    send_welcome(message)


func_dict = {
    'Back home': go_home
    ,'Training Vocabulary': training_vocabulary
    # ,'Add new word': add_new_word
}


def func(message, bot):
    func_dict[message.text](message, bot)


def training(message, bot):
    global_var.status = message.text
    print(global_var.status)

    modes = ['Training Vocabulary', 'Writing', 'Back home']
    markup = utils.generate_markup(modes)
    message = bot.send_message(
        message.chat.id
        ,f"What do you want to practice?"
        ,reply_markup=markup
    )
    bot.register_next_step_handler(message, func, bot)

def add_new_word(message, bot):
    def bot_save_new_word(new_word, tablename, dbname):
        global_var.app = App.App()
        app = global_var.app
        res = app.is_new_word_in_db(new_word, tablename, dbname)
        
        app.save_new_word(new_word, tablename, dbname)

    def client_enter_word(message, bot):
        global_var.new_word['word'] = message.text
        bot_asks_translation(message, bot)

    def client_enter_translation(message, bot):
        global_var.new_word['translation'] = message.text
        bot_asks_if_word_and_translation_are_correct(message, bot)

    def client_answers_if_word_and_translation_are_correct(message, bot):
        answer = message.text
        if answer == 'Yes':
            message = bot.send_message(
                message.chat.id,
                f"Great!"
            )
            # bot_save_new_word(global_var.new_word, app.dict_table_name, app.dbname)
            global_var.app = App.App()
            app = global_var.app
            res, table = app.is_new_word_in_db(global_var.new_word, app.dict_table_name, app.dbname)
            if res == False:
                app.save_new_word(global_var.new_word, app.dict_table_name, app.dbname)
                global_var.new_word = {
                    'word': '',
                    'translation': '' 
                }
                go_home(message)
            else:
                bot_asks_if_client_want_to_add_new_word_that_already_exists(message, bot, table)

        elif answer == 'No':
            message = bot.send_message(
                message.chat.id,
                f"Try again"
            )
            add_new_word(message, bot)
        elif answer == 'Back home':
            new_word = {
                'word': '',
                'translation': '' 
            }
            go_home(message)

    def cient_answers_if_client_want_to_add_new_word_that_already_exists(message, bot):
        answer = message.text
        message = bot.send_message(
            message.chat.id,
            f"Okay!"
        )
        if answer == 'Yes':
            global_var.app = App.App()
            app = global_var.app
            app.save_new_word(global_var.new_word, app.dict_table_name, app.dbname)
            global_var.new_word = {
                'word': '',
                'translation': '' 
            }
            go_home(message)
        elif answer == 'No':
            new_word = {
                'word': '',
                'translation': ''
            }
            go_home(message)

    def bot_asks_word(message, bot):
        message = bot.send_message(
            message.chat.id,
            "Enter word",
            reply_markup = types.ReplyKeyboardRemove(),
        )
        bot.register_next_step_handler(message, client_enter_word, bot)

    def bot_asks_translation(message, bot):
        message = bot.send_message(
            message.chat.id,
            "Enter translation",
        )
        bot.register_next_step_handler(message, client_enter_translation, bot)

    def bot_asks_if_word_and_translation_are_correct(message, bot):
        text = f"You entered:\nWord: {global_var.new_word['word']}\nTranslation: {global_var.new_word['translation']}\nIs everything right?"
        message = bot.send_message(
            message.chat.id,
            text,
            reply_markup = utils.generate_markup()
        )
        bot.register_next_step_handler(message, client_answers_if_word_and_translation_are_correct, bot)

    def bot_asks_if_client_want_to_add_new_word_that_already_exists(message, bot, table):
        text_i = lambda new_word: f"Word: {new_word['Word']}\nTranslation: {new_word['Translation']}\n"

        text = [text_i(table.iloc[i]) for i in range(0, len(table))]
        text = '\n'.join(text)

        text = f"You have already added this words!\n\n{text}\nDo you really want to add new word?"
        message = bot.send_message(
            message.chat.id,
            text,
            reply_markup = utils.generate_markup(['Yes', 'No'])
        )
        bot.register_next_step_handler(message, cient_answers_if_client_want_to_add_new_word_that_already_exists, bot)

    global_var.status = message.text
    print(global_var.status)

    bot_asks_word(message, bot)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    print('sdfsdfsdf s')
    print(call.data)


bot.polling()
