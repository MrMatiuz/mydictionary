import telebot
from telebot import types

import numpy as np
import time

import App

TOKEN = '5943330094:AAFYsy1OuQOIjUPjUwjyJz4xYa3rQ9GS3zs'


bot = telebot.TeleBot(TOKEN)

user_dict = {}


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Hi there, I am Example bot.
What's your name?
""")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    
    chat_id = message.chat.id
    name = message.text
    user = User(name)
    user_dict[chat_id] = user
    msg = bot.reply_to(message, 'How old are you?')
    bot.register_next_step_handler(msg, process_age_step)
    # except Exception as e:
    #     bot.reply_to(message, 'oooops')


def process_age_step(message):
    chat_id = message.chat.id
    age = message.text
    if not age.isdigit():
        msg = bot.reply_to(message, 'Age should be a number. How old are you?')
        bot.register_next_step_handler(msg, process_age_step)
        return
    user = user_dict[chat_id]
    user.age = age
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Male', 'Female')
    msg = bot.send_message(message.chat.id, 'What is your gender', reply_markup=markup)
    bot.register_next_step_handler(msg, process_sex_step)
    # except Exception as e:
    #     bot.reply_to(message, 'oooops')


def process_sex_step(message):
    try:
        chat_id = message.chat.id
        sex = message.text
        user = user_dict[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception("Unknown sex")
        bot.send_message(chat_id, 'Nice to meet you ' + user.name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
    except Exception as e:
        bot.reply_to(message, 'oooops')


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

bot.infinity_polling()
Footer


# bot = telebot.TeleBot(TOKEN)

# def check_word(app ,indx=None, inverse=False):
#     activity = dict(zip(
#         app.activities_params
#         ,[np.nan]*len(app.activities_params)
#     ))
    
#     word_and_translation = app.get_word_and_translation(indx)
#     indx = word_and_translation[0]
#     if inverse == True:
#         word, translation = word_and_translation[1::-1]
#     elif inverse == False:
#         word, translation = word_and_translation[1::]
#     else:
#         raise TypeError("Only booleans are allowed in inverse")
        
#     print(f"Word is '{translation}'.\nWhat is its translation? To see translation press Enter.")
#     start = time.time()
#     while True:
#         check_if_press_enter = input()
#         break
#     print(f"Translation is '{word}'.", end=' ')
#     end = time.time()
#     elapsed_time = end - start # time to answer the question
    
#     answer = app.check_if_answer_was_correct(question='Was your answer correct?')
    
#     activity['id'] = str(indx)
#     activity['Success'] = str(answer)
#     activity['Elapsed_time'] = str(elapsed_time)
    
#     return activity

# def generate_markup():
# 	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
# 	for item in ['Yes', 'No']:
# 		markup.add(item)
# 	return markup

# @bot.message_handler(commands=['start'])
# def send_welcome(message):
#     # Send a message with the keyboard
# 	bot.reply_to(message, "Hello! Let's start training")
# 	markup = generate_markup()
# 	bot.send_message(message.chat.id, '1', reply_markup=markup)

# # @bot.message_handler(commands=['start_training'])
# # def send_welcome(message):
# #     # Create a keyboard with two buttons
# #     # keyboard = types.InlineKeyboardMarkup()
# #     # button_yes = types.InlineKeyboardButton('Yes', callback_data='button_yes')
# #     # button_no = types.InlineKeyboardButton('No', callback_data='button_no')
# #     # keyboard.add(button_yes, button_no)

# # 	markup = generate_markup()
# #     bot.send_message(message.chat.id, '1', reply_markup=markup)
# # 	# bot.reply_to(message, f"Word is '{translation}'.\nDo you now translation?", reply_markup=keyboard)


# #     # vocabulary_name = 'Words.xlsx'
# #     # app = App.App(vocabulary_name)
# #     # app.read_file()

# #     # random = True
# #     # inverse = False
# #     # if random == True:
# #     #     indx = app.get_random_indx()[0]
# #     # else:
# #     #     Rand = wr.Ranging()
# #     #     word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
# #     #     word_indxs = app.get_random_indx(word_indxs)

# #     # i = 0
# #     # activity = app.check_word(word_indxs[i])
# #     # =====================================================================================================
# #     # activity = dict(zip(
# #     #     app.activities_params
# #     #     ,[np.nan]*len(app.activities_params)
# #     # ))
    
# #     # word_and_translation = app.get_word_and_translation(indx)
# #     # indx = word_and_translation[0]
# #     # if inverse == True:
# #     #     word, translation = word_and_translation[1::-1]
# #     # elif inverse == False:
# #     #     word, translation = word_and_translation[1::]
# #     # else:
# #     #     raise TypeError("Only booleans are allowed in inverse")
        
# #     # print()
# #     # bot.reply_to(message, f"Word is '{translation}'.\nDo you now translation?", reply_markup=keyboard)
# #     # start = time.time()
# #     # bot.reply_to(message, f"Translation is '{word}'.")
# #     # end = time.time()
# #     # elapsed_time = end - start # time to answer the question
    
# #     # bot.reply_to(message, f"Was your answer correct?", reply_markup=keyboard)
# #     # # answer = app.check_if_answer_was_correct(question='Was your answer correct?')
    
# #     # activity['id'] = str(indx)
# #     # activity['Success'] = str(answer)
# #     # activity['Elapsed_time'] = str(elapsed_time)
# #     # =====================================================================================================
# #     # Send a message with the keyboard


# @bot.callback_query_handler(func=lambda call: True)
# def handle_callback_query(call):
#     # Handle button callbacks
# 	print(call.data)

#     # if call.data == 'button_yes':
#     #     bot.answer_callback_query(call.id, text='You pushed button 1')
#     # elif call.data == 'button_no':
#     #     bot.answer_callback_query(call.id, text='You pushed button 2')

# bot.polling()
