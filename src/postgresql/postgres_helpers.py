import json
import psycopg2


def consume_initial(msg):
    conn = psycopg2.connect(database='sherlockdb', 
                            user='postgres', 
                            host='localhost', 
                            port='1324', 
                            password='default')

    curs = conn.cursor()
    sql = """INSERT INTO model_info (model_name, imageset_name) VALUES (%s,%s) RETURNING model_id;"""
    dir = msg['bucket_prefix'].split('/')
    model_name = dir[-1]
    
    curs.execute(sql, (model_name, msg['imageset_name']))
    model_id = curs.fetchone()[0]
    conn.commit()
    curs.close()
    conn.close()
    return model_id

def consume_update(model_info):
    conn = psycopg2.connect(database='sherlockdb',
                            user='postgres',
                            host='localhost',
                            port='1324',
                            password='default')


    
    curs = conn.cursor()
    classes = model_info['classes']
    sql = """UPDATE model_info SET classes = %s;"""
    curs.execute(sql, (json.dumps(classes),))
    conn.commit()
    curs.close()
    conn.close()