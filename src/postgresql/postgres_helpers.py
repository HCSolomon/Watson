import json
import psycopg2
import uuid


def consume_upsert(msg):
        conn = psycopg2.connect(database='sherlockdb', 
                                user='postgres', 
                                host='ec2-34-220-127-34.us-west-2.compute.amazonaws.com', 
                                port='1324', 
                                password='default')

        curs = conn.cursor()
        sql = """UPDATE model_info SET classes = %s WHERE model_id=%s; 
                INSERT INTO model_info (model_name, model_id, imageset_name, classes)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM model_info WHERE model_id=%s);"""
        params = (json.dumps(msg['classes']), 
                msg['model_id'], 
                msg['model_name'],
                msg['model_id'],
                msg['imageset_name'],
                json.dumps(msg['classes']),
                msg['model_id']
                )
        curs.execute(sql, params)
        conn.commit()
        curs.close()
        conn.close()
        return msg['model_id']