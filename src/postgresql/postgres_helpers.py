import json
import psycopg2
from psycopg2 import sql
import uuid


def consume_upsert(msg):
        conn = psycopg2.connect(database='watsondb', 
                                user='postgres', 
                                host='localhost', 
                                port='1324', 
                                password='default')

        curs = conn.cursor()
        sql = """UPDATE model_info SET classes = %s WHERE model_name = %s; 
                INSERT INTO model_info (model_name, imageset_name, classes)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM model_info WHERE model_name = %s);"""
        params = (json.dumps(msg['classes']),
                msg['model_name'],
                msg['model_name'],
                msg['imageset_name'],
                json.dumps(msg['classes']),
                msg['model_name']
                )
        curs.execute(sql, params)
        conn.commit()
        curs.close()
        conn.close()

def label_calcs(labels):
        cls_count = {}
        sum_probs = 0
        prob_count = 0
        for item in labels:
                cls_count[item[0]['label']] = cls_count.get(item[0]['label'], 0) + 1
                sum_probs += item[0]['prob']
                prob_count += 1
        
        return cls_count, sum_probs/prob_count

def stat_update(model_name, cls_count):
        conn = psycopg2.connect(database='watsondb', 
                                user='postgres', 
                                host='localhost', 
                                port='1324', 
                                password='default')
        curs = conn.cursor()
<<<<<<< HEAD
        sql = psycopg2.sql
        sql_table = sql.SQL("""CREATE TABLE IF NOT EXISTS {} (
                label text, 
                count integer, 
                PRIMARY KEY label
                );""").format(sql.Identifier('sherlockdb'))
        curs.execute(sql_table)
        conn.commit()
=======
>>>>>>> ab3d6e1b0a84923e211e8767bec95ec0c35b3de9
        for label in cls_count:
                sql_update = """INSERT INTO label_count(model_name, label, count)
                                VALUES(%s, %s, %s)
                                ON CONFLICT (model_name, label) DO UPDATE
                                SET count = label_count.count + %s 
                                WHERE (label_count.model_name, label_count.label)= (%s, %s);"""
                params = (model_name,
                        label,
                        cls_count[label],
                        cls_count[label],
                        model_name,
                        label)
                curs.execute(sql_update, params)
                print(label)
                conn.commit()
        curs.close()
        conn.close()

def main():
        with open('samples/list_test.json') as f:
                j = json.loads(f.read())

        cls_count, avg_prob = label_calcs(j)
        stat_update('test', cls_count)

if __name__ == "__main__":
        main()