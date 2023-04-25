import numpy as np
import pandas as pd
import random
import time

import csv
import os

import Word_Ranking as wr
# import keyboard

class App:
    def __init__(self, name):
        self.name = name
        self.df = None
        self.activities_params = [
            'id'
            ,'Success'
            ,'Elapsed_time'
        ]
        self.client_activities = []
        self.batch_size = 5
    
    def read_file(self):
        '''
        Пока не будем работать с базой, будем брать весь датафрейм и его менять,
        а потом просто перезаливать базу. Позже реализовать алгоритм, который будет выборочно либо добавлять,
        либо перезаписывать данные по конекретным колонкам
        '''
        self.df = pd.read_excel(self.name)

        self.df['Word'] = self.df['Word'].apply(lambda x: x.capitalize())
        self.df['Translation'] = self.df['Translation'].apply(lambda x: x.capitalize())
        self.df.fillna(0, inplace=True)


    def push_new_word(self):
        word = input("Enter word: ")
        translation = input("Enter translation: ")


    def get_random_indx(self, indxs=None):
        get_random_indx_from_df = lambda df, batch_size: (
            np.array(df \
                .sample(n=batch_size) \
                .index)
        )
        
        if indxs is None:
            indxs = get_random_indx_from_df(self.df, self.batch_size)
        else:
            indxs_len = len(indxs)
            if len(indxs) < self.batch_size:
                extra_indxes = get_random_indx_from_df(self.df, self.batch_size - indxs_len)
                indxs = np.concatenate((indxs, extra_indxes), axis=0)

        return indxs


    def get_word_and_translation(self, indx):
        # Getting random word
        # word_and_translation = self.df.sample(n=1)
        word_and_translation = self.df.loc[indx]

        return [
            word_and_translation['id']
            ,word_and_translation['Word']
            ,word_and_translation['Translation']
        ]
    
    
    def check_if_answer_was_correct(self, question):
        answer = input(f"{question} (y/n): ")
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print(f"Didn't get your answer '{answer}'. Try agane. ", end="")
            return self.check_if_answer_was_correct(question)

    
    def inverse_translation(self, word_and_translation, inverse):
        indx = word_and_translation[0]
        if inverse == True:
            word, translation = word_and_translation[1::-1]
        elif inverse == False:
            word, translation = word_and_translation[1::]
        else:
            raise TypeError("Only booleans are allowed in inverse")
        return indx, word, translation

    def server_asks_about_trainslation(self, indx, word, translation):
        print(f"Word is '{translation}'.\nWhat is its translation? To see translation press Enter.")
        return time.time()

    def client_answers_about_translation(self, indx, word, translation):
        while True:
            check_if_press_enter = input()
            break
        print(f"Translation is '{word}'.", end=' ')
        return time.time()


    def elapsed_time(self, indx, word, translation):
        # client-server chat
        start = self.server_asks_about_trainslation(indx, word, translation)
        end = self.client_answers_about_translation(indx, word, translation)
        answer = self.check_if_answer_was_correct(question='Was your answer correct?')
        __continue__ = self.check_if_answer_was_correct(question='Continue?')
        return __continue__, answer, end - start


    def check_word(self,  indx, chat_func, inverse, message=None, bot=None):
        # init activity dict
        activity = dict(zip(
            self.activities_params
            ,[np.nan]*len(self.activities_params)
        ))
        
        word_and_translation = self.get_word_and_translation(indx)
        indx, word, translation = self.inverse_translation(word_and_translation, inverse)
        try:
            __continue__, answer, elapsed_time = chat_func(message, bot, indx, word, translation)
        except:
            __continue__, answer, elapsed_time = self.elapsed_time(indx, word, translation)
        # chat_func(self, indx, word, translation, default)
        # elapsed_time = chat_func(self, indx, word, translation, default)

        if __continue__ == True:
            # Write result
            activity['id'] = str(indx)
            activity['Success'] = str(answer)
            activity['Elapsed_time'] = str(elapsed_time)
            return activity
        elif __continue__ == False:
            return False
            
    def get_indxs(self, random):
        if random == True:
            word_indxs = self.get_random_indx()
        else:
            Rand = wr.Ranging()
            word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
            word_indxs = self.get_random_indx(word_indxs)
        return word_indxs


    # def check_your_vocabulary(self, random=False, inverse=False, default=True):
    #     print(f"Let's start training!")
    #     word_indxs = self.get_indxs(random)
        
    #     i = 0
    #     while True :
    #         activity = self.check_word(word_indxs[i], inverse=inverse, default=default)
    #         self.client_activities += [activity]
    #         answer = self.check_if_answer_was_correct(question='Continue?')
    #         if answer == False:
    #             break
    #         if i == self.batch_size - 1:
    #             print("saving logs")
    #             self.write_user_activities_logs(self.client_activities)
    #             self.client_activities = []

    #             if random == True:
    #                 word_indxs = self.get_random_indx()
    #             else:
    #                 Rand = wr.Ranging()
    #                 word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
    #                 word_indxs = self.get_random_indx(word_indxs)
                
    #             i = 0

    #         i += 1
                    
    #     self.write_user_activities_logs(self.client_activities)

    def training_vocabulary(self, random=False, inverse=False, chat_func=elapsed_time):

        word_indxs = self.get_indxs(random)
        i = 0
        while True :
            activity = self.check_word(indx=word_indxs[i], inverse=inverse, chat_func=chat_func)
            if activity == False:
                break
            self.client_activities += [activity]
            if i == self.batch_size - 1:
                print("saving logs")
                self.write_user_activities_logs(self.client_activities)
                self.client_activities = []

                word_indxs = self.get_indxs(random)
                i = 0

            i += 1
                    
        self.write_user_activities_logs(self.client_activities)

    
    def write_user_activities_logs(self, client_activities, file_name ='user_activities_logs.csv'):
        isExist = os.path.exists(file_name)
        
        with open(file_name, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=self.activities_params, lineterminator="\n")
            if isExist == False:
                writer.writeheader()
            
            f.write('\n')
            for row in client_activities:
                writer.writerow(row)
            
            f.close()

    
    def save_file(self):
        self.df.to_excel(self.name)