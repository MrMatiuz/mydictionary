import telebot
from telebot import types

import time

import config
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
            pass
    elif global_var.status == 'training_vocabulary':
        training_vocabulary(message, bot)
    elif global_var.status == 'checking_word':
        print('============================================================')


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
            # global_var.__continue__, global_var.answer, global_var.end = False, None, None
            print("saving logs")
            app.write_user_activities_logs(app.client_activities)
            # app.client_activities = []
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
            global_var.__continue__, global_var.answer, global_var.end = True, utils.true_false_answer[answer], time.time()
            global_var.elapsed_time = global_var.end - global_var.start
            global_var.__if_client_answered__ = True
            
            time.sleep(1.5)
            training_process(message, bot)


def chat_func(message, bot, indx, word, translation):
    global_var.status = 'checking_word'
    bot_asks_about_trainslation(message, bot, indx, word, translation)

    return True, None, None


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
            app.write_user_activities_logs(app.client_activities)
            app.client_activities = []

            global_var.word_indxs = app.get_indxs(random)
            i = 0
                
    # self.write_user_activities_logs(self.client_activities)


def training_vocabulary(message, bot):
    global_var.status = 'training_vocabulary'
    print(global_var.status)
    # ================================================================================================
    vocabulary_name = 'Words.xlsx'
    app = App.App(vocabulary_name)
    app.read_file()
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
    ,'Add new word': training_writing
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

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    print('sdfsdfsdf s')
    print(call.data)


bot.polling()
