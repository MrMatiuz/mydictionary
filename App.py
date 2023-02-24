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
        self.batch_size = 20
    
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
            word_and_translation['id'].values[0]
            ,word_and_translation['Word'].values[0]
            ,word_and_translation['Translation'].values[0]
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
    
    
    def check_word(self, indx=None, inverse=False):
        activity = dict(zip(
            self.activities_params
            ,[np.nan]*len(self.activities_params)
        ))
        
        word_and_translation = self.get_word_and_translation(indx)
        indx = word_and_translation[0]
        if inverse == True:
            word, translation = word_and_translation[1::-1]
        elif inverse == False:
            word, translation = word_and_translation[1::]
        else:
            raise TypeError("Only booleans are allowed in inverse")
            
        print(f"Word is '{translation}'.\nWhat is its translation? To see translation press Enter.")
        start = time.time()
        while True:
            check_if_press_enter = input()
            break
        print(f"Translation is '{word}'.", end=' ')
        end = time.time()
        elapsed_time = end - start # time to answer the question
        
        answer = self.check_if_answer_was_correct(question='Was your answer correct?')
        
        activity['id'] = str(indx)
        activity['Success'] = str(answer)
        activity['Elapsed_time'] = str(elapsed_time)
        
        return activity

#         # Correstion accuracy metric
#         if answer == True:
#             self.df.loc[indx, 'TriesNum'] += 1
#             self.df.loc[indx, 'SuccessesNum'] += 1
#         elif answer == False:
#             self.df.loc[indx, 'TriesNum'] += 1
#         self.df.loc[indx, 'Probability'] = 1 - self.df.loc[indx, 'SuccessesNum'] / self.df.loc[indx, 'TriesNum']
                
#         # Correction distibution params
#         self.df.loc[indx, 'MeanTime'] = (
#             (self.df.loc[indx, 'MeanTime'] * (self.df.loc[indx, 'TriesNum'] - 1) + elapsed_time) \
#             / self.df.loc[indx, 'TriesNum']
#         )     
#         if elapsed_time > self.df.loc[indx, 'MaxTime'].values[0]:
#             self.df.loc[indx, 'MaxTime'] = elapsed_time
#         elif elapsed_time < self.df.loc[indx, 'MinTime'].values[0]:
#             self.df.loc[indx, 'MinTime'] = elapsed_time
            
    
    def check_your_vocabulary(self):
        print(f"Let's start training!")
        Rand = wr.Ranging()
        word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
        word_indxs = self.get_random_indx(word_indxs)

        i = 0
        while True :
            activity = self.check_word(word_indxs)
            self.client_activities += [activity]
            answer = self.check_if_answer_was_correct(question='Continue?')
            if answer == False:
                break
            if i == self.batch_size:
                print("saving logs")
                self.write_user_activities_logs(self.client_activities)
                self.client_activities = []

                Rand = wr.Ranging()
                word_indxs = Rand.get_ranked_words('user_activities_logs.csv')
                word_indxs = self.get_random_indx(word_indxs)

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