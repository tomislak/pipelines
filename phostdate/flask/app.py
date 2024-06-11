import psycopg2
from flask import Flask, render_template
import platform
from datetime import datetime

def connectToPostgres():
    #return psycopg2.connect(database='postgres', user='postgres', password='hostdate', host='localhost', port='5432')
    return psycopg2.connect(database='postgres', user='postgres', password='hostdate', host='postgres', port='5432')

def connectToDb(db_name, db_user, db_passwd, db_host):
    return psycopg2.connect(database=db_name, user=db_user, password=db_passwd, host=db_host, port='5432')

def insertToDb(nodeName, timeNow):
    conn = None
    try:
        print('Connecting to the hostdate database...')
        #conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'localhost')
        conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'postgres')
        cur = conn.cursor()
        print('Inserting into hostdate table')
        sql = """ INSERT INTO hostdate (stringhost, stringdate) VALUES (%s, %s)"""
        pod = (nodeName, timeNow)
        cur.execute(sql, pod)
        conn.commit()
        cur.close()

        reza = "OK"
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        reza = error
    finally:
        if conn is not None:
            conn.close()
        return 'data insert: ' + str(reza)

def selectLast10():
    conn = None
    try:
        polje = []
        print('Connecting to the hostdate database...')
        #conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'localhost')
        conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'postgres')
        cur = conn.cursor()
        print('Select last 10 rows')
        sql = """SELECT * FROM hostdate ORDER BY id DESC LIMIT 10;"""
        cur.execute(sql)
        for red in cur.fetchall():
            polje.append(red)
        conn.commit()
        cur.close()

        reza = "OK"
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        reza = error
    finally:
        if conn is not None:
            conn.close()
        return 'data select: ' + str(reza), polje

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/pingDb')
def pingDb():
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = connectToPostgres()
        cur = conn.cursor()
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        reza = cur.fetchone()
        print(reza)
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        reza = error
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    return 'database connection: ' + str(reza)

@app.route('/prepareDb')
def prepareDb():
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = connectToPostgres()
        conn.autocommit = True
        cur = conn.cursor()
        print('Creating hostdate user')
        sql = """create role hostdate createdb login password 'hostdate';"""
        cur.execute(sql)
        conn.commit()
        print('Creating hostdate database')
        sql = """create database hostdate with owner = hostdate;"""
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

        print('Connecting to the hostdate database...')
        conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'postgres')
        #conn = connectToDb('hostdate', 'hostdate', 'hostdate', 'localhost')
        cur = conn.cursor()
        print('Creating hostdate table')
        sql = '''create table hostdate(
          id bigserial primary key,
          stringhost VARCHAR(100),
          stringdate VARCHAR(100)
        );'''
        cur.execute(sql)
        conn.commit()
        cur.close()

        reza = "OK"
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        reza = error
    finally:
        if conn is not None:
            conn.close()
        return 'database preparation: ' + str(reza)

@app.route('/hostDate')
def get_hostDate():
    return render_template('index.html', node_name=str(platform.node()), date_now=str(datetime.now().isoformat()))

@app.route('/hostDateDb')
def insertHostDate():
    nodeName = str(platform.node())
    timeNow = str(datetime.now().isoformat())
    rezaI = insertToDb(nodeName, timeNow)
    rezaS, polje = selectLast10()
    return render_template('insert.html', node_name=nodeName, date_now=timeNow, rezultatI=rezaI, polje=polje, rezultatS=rezaS)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
