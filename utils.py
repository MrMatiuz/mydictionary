import telebot
from telebot import types

import App

base_answers = {
    'Yes': 'Great!',
    'No': 'Nothing to worry, everything is fine!',
    'Back home': 'Back home'
}

true_false_answer = {
    'Yes': True,
    'No': False
}

def generate_markup(answers=['Yes', 'No', 'Back home']):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    markup.add(*answers, row_width=2)
    # for item in answers:
    #     button = types.KeyboardButton(item)
    #     # button = types.InlineKeyboardButton(item, callback_data='button_'+item)
    #     markup.add(button)
    return markup