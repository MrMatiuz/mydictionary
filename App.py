import numpy as np
import pandas as pd
import random
import time

import csv
import sqlite3
import os

import Word_Ranking as wr
# import keyboard


class App:
    def __init__(self, dict_table_name='dict', logs_table_name='user_activities_logs', dbname='mydictionary.db'):
        self.activities_params = [
            'id'
            ,'Success'
            ,'Elapsed_time'
        ]
        self.client_activities = []
        self.batch_size = 5
        self.dict_table_name = dict_table_name
        self.logs_table_name = logs_table_name
        self.dbname = dbname

        self.df = self.read_vocabulary(self.dict_table_name, self.dbname)


    def drop_file_extension(self, filename):
        filename_inv = filename[::-1]
        dot_pos = filename_inv.find('.') + 1

        if dot_pos == 0:
            return filename
        else:
            return filename[:-dot_pos]


    def read_vocabulary(self, tablename, dbname):
        tablename = self.drop_file_extension(tablename)
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        table = pd.read_sql_query(f"SELECT * from {tablename}", conn)
        conn.close()
        return table


    # def read_vocabulary(self):
    #     '''
    #     Пока не будем работать с базой, будем брать весь датафрейм и его менять,
    #     а потом просто перезаливать базу. Позже реализовать алгоритм, который будет выборочно либо добавлять,
    #     либо перезаписывать данные по конекретным колонкам
    #     '''
    #     self.df = pd.read_excel(self.name)

    #     self.df['Word'] = self.df['Word'].apply(lambda x: x.capitalize())
    #     self.df['Translation'] = self.df['Translation'].apply(lambda x: x.capitalize())
    #     self.df.fillna(0, inplace=True)


    # def push_new_word(self):
    #     word = input("Enter word: ")
    #     translation = input("Enter translation: ")


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
            activity['id'] = int(indx)
            activity['Success'] = int(answer)
            activity['Elapsed_time'] = elapsed_time
            return activity
        elif __continue__ == False:
            return False
            
    def get_indxs(self, random):
        if random == True:
            word_indxs = self.get_random_indx()
        else:
            Rand = wr.Ranging()
            word_indxs = Rand.get_ranked_words(tablename=self.logs_table_name, dbname=self.dbname)
            word_indxs = self.get_random_indx(word_indxs)
        return word_indxs


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
                    
        self.write_user_activities_logs(self.client_activities, self.logs_table_name, self.dbname)

    
    def write_user_activities_logs(self, client_activities, tablename, dbname):
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        for row in client_activities:
            cursor.execute(
                f"INSERT INTO {tablename} (id, Success, Elapsed_time) VALUES (?, ?, ?)", 
                (row['id'], row['Success'], row['Elapsed_time'])
            )
        conn.commit()
        conn.close()

    def is_new_word_in_db(self, new_word, tablename, dbname):
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        
        word = new_word['word'].lower()
        for s in ['to ', 'a ']:
            word = word.replace(s, '')

        query = (
            f"SELECT * \
            FROM {tablename} \
            WHERE \
                Word LIKE '%{word}' \
                or Word LIKE '%{word} %'"
        )
        table = pd.read_sql_query(query, conn)
        if table.empty:
            return False, None
        else:
            return True, table


    def save_new_word(self, new_word, tablename, dbname):
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        query = f"SELECT max(id) FROM {tablename}"

        last_row = cursor.execute(query).fetchone()[0]
        new_id = last_row + 1
        word = new_word['word']
        translation = new_word['translation']

        query = f"INSERT INTO {tablename} (id, Word, Translation) VALUES (?, ?, ?)"
        cursor.execute(
                query, 
                (new_id, word, translation)
            )
        conn.commit()
        conn.close()