import pandas as pd
import numpy as np
import csv
import os
import sqlite3


class Ranging():
    def __init__(self):        
        self.x_last = 0
        self.x_critical = 0
        self.a = 0.5
        self.b = 0.5


    def metric(self, x):
        x_last = self.x_last
        x_critical = self.x_critical

        if x >= 0:
            if x >= x_last:
                return 0
            else:
                if x < x_critical:
                    return -1 / (x_last * x_critical) * x**2 + 1
                else:
                    return -x / x_last + 1
        else:
            # return 1
            raise Exception('Unexpected time values < 0')

    def probability(self, accuracy, metric):
        a = self.a
        b = self.b

        return a * accuracy + b * metric

    # def accuracy(self, x_true, x_all):
    #     return x_true / x_all


    def get_logs(self, tablename, dbname):
        conn = sqlite3.connect(dbname)
        cursor = conn.cursor()
        table = pd.read_sql_query(f"SELECT * from {tablename}", conn)
        conn.close()
        return table


    def update_metrisc(self, logs_df=None, logs_grouped_by_id=None):
        x_true_prob = 0.5

        x_true_indxs = logs_grouped_by_id[logs_grouped_by_id[('Success', 'accuracy')] >= x_true_prob].index.values
        x_true_df = logs_df[
            (logs_df['id'].isin(x_true_indxs))
            & (logs_df['Success'] == True)
        ]

        max = x_true_df['Elapsed_time'].max()
        mean = x_true_df['Elapsed_time'].mean()
        std = x_true_df['Elapsed_time'].std()
        
        x_last = max
        x_critical = mean + std

        return x_last, x_critical

    def get_ranked_words(self, tablename, dbname):
        try:
            logs_df = self.get_logs(tablename, dbname)
        except:
            return None

        logs_grouped_by_id = logs_df \
            .groupby(by=['id']) \
            .agg({
                'Success':['sum', 'count']
                ,'Elapsed_time':['mean']
                })

        logs_grouped_by_id[('Success', 'accuracy')] = logs_grouped_by_id[('Success', 'sum')] / logs_grouped_by_id[('Success', 'count')]

        self.x_last, self.x_critical = self.update_metrisc(logs_df, logs_grouped_by_id)
        logs_grouped_by_id[('Elapsed_time', 'metrics')] = logs_grouped_by_id[('Elapsed_time', 'mean')].apply(self.metric)

        logs_for_prob = logs_grouped_by_id[[
            ('Success', 'accuracy')
            ,('Elapsed_time', 'metrics')
        ]]
        prob = [self.probability(a_i, m_i) for a_i, m_i in logs_for_prob.values]
        logs_grouped_by_id['Probability'] = prob
        logs_grouped_by_id.sort_values(by='Probability', ascending=False, inplace=True)

        # logs_grouped_by_id['Probsbility'] = logs_grouped_by_id[[('Success', 'accuracy'), ('Elapsed_time', 'metrics')]]. \
            # apply(lambda df: self.probability(df[('Success', 'accuracy')], df[('Elapsed_time', 'metrics')]), axis=1)
        return np.array(logs_grouped_by_id.index)



if __name__ == "__main__":
    import time

    start = time.time()
    r = Ranging()
    # r.update_metrisc()
    res = r.get_ranked_words(tablename = 'user_activities_logs', dbname = 'mydictionary.db')
    end = time.time()
    print(f"TIME: {end - start} sec.")
    print(res)
