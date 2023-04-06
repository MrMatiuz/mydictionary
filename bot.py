import telebot
from telebot import types

import time

import config
import global_var
import utils

import App


# status = None

TOKEN = config.token
bot = telebot.TeleBot(TOKEN)

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
        if message.text in utils.base_answers.keys():
            if message.text == 'Back home':
                go_home(message)
            else:
                message = bot.send_message(
                    message.chat.id
                    ,utils.base_answers[message.text]
                )
                time.sleep(1.5)
                training_vocabulary(message, bot)

def chat_func(message, bot, word):
    markup = utils.generate_markup()
    message = bot.send_message(
        message.chat.id
        ,f"Do you know word {word}?"
        ,reply_markup=markup
    )

def training_vocabulary(message, bot):
    global_var.status = 'training_vocabulary'
    print(global_var.status)

    # ================================================================================================
    vocabulary_name = 'Words.xlsx'
    app = App.App(vocabulary_name)
    app.read_file()
    
    word_indxs = app.get_indxs(random=True)
    app.check_word(indx=word_indxs[0], chat_func=chat_func, message=message, bot=bot)
    # ================================================================================================
    # markup = utils.generate_markup()
    # message = bot.send_message(
    #     message.chat.id
    #     ,f"Do you know word {word}?"
    #     ,reply_markup=markup
    # )

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




# @bot.message_handler(commands=['start_training_vocabulary'])
# def send_welcome(message):
#     # Send a message with the keyboard
#     bot.reply_to(message, "Hello! Let's start training")
#     markup = generate_markup()
#     bot.send_message(message.chat.id, '1', reply_markup=markup)

# @bot.message_handler(commands=['start_training'])
# def send_welcome(message):
#     # Create a keyboard with two buttons
#     # keyboard = types.InlineKeyboardMarkup()
#     # button_yes = types.InlineKeyboardButton('Yes', callback_data='button_yes')
#     # button_no = types.InlineKeyboardButton('No', callback_data='button_no')
#     # keyboard.add(button_yes, button_no)

# 	markup = generate_markup()
#     bot.send_message(message.chat.id, '1', reply_markup=markup)
# 	# bot.reply_to(message, f"Word is '{translation}'.\nDo you now translation?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    print('sdfsdfsdf s')
    print(call.data)

    # if call.data == 'button_yes':
    #     bot.answer_callback_query(call.id, text='You pushed button 1')
    # elif call.data == 'button_no':
    #     bot.answer_callback_query(call.id, text='You pushed button 2')

bot.polling()
