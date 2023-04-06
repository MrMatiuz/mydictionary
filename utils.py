import telebot
from telebot import types

import App

base_answers = {
    'Yes': 'Great!'
    ,'No': 'Nothing to worry, everything is fine!'
    ,'Back home': 'Back home'
}

def generate_markup(answers=['Yes', 'No', 'Back home']):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for item in answers:
        button = types.KeyboardButton(item)
        # button = types.InlineKeyboardButton(item, callback_data='button_'+item)
        markup.add(button)
    return markup

def check_your_vocabulary(random=True):
    vocabulary_name = 'Words.xlsx'
    app = App.App(vocabulary_name)
    app.read_file()

    
    if random == True:
        word_indxs = app.get_random_indx()
    else:
        Rand = wr.Ranging()
        word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
        word_indxs = self.get_random_indx(word_indxs)




# ===========================================================================================

# def delete_queastion_answer(previous_message, message):
#     bot.delete_message(previous_message.chat.id, previous_message.message_id)
#     bot.delete_message(message.chat.id, message.message_id)

# def check_word(message, app, indx, inverse=False):
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
    
#     msg = bot.send_message(
#         message.chat.id
#         ,f"Word is '{translation}'.\nDo you know its translation?"
#         ,reply_markup=generate_markup()
#     )

#     # print(msg)
#     return

#     if msg.text == 'Yes':
#         msg = bot.send_message(
#             message.chat.id
#             ,f"Graet! Continue?"
#             ,reply_markup=generate_markup()
#         )
#         bot.register_next_step_handler(msg, check_word(msg, app, indx))
        
#     elif msg.text == 'No':
#         msg = bot.send_message(
#             message.chat.id
#             ,f"Nothing to worry, everything is fine! Continue?"
#             ,reply_markup=generate_markup()
#         )
#         bot.register_next_step_handler(msg, check_word(msg, app, indx))


# def training_vocabulary(message):
#     vocabulary_name = 'Words.xlsx'
#     app = App.App(vocabulary_name)
#     app.read_file()
#     word_indxs = app.get_random_indx()

#     i = 0
#     while True :
#         activity = check_word(message, app, word_indxs[i])         
#         break