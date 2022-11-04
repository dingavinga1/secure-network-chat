import socket
import threading
import sys
import time

from rsa import generateKeys, encryptString, decryptString
sys.setrecursionlimit(2147483647)

""" Each client in the chat network """

dnsBuff=''
dnsReply=''
dnsBuffMutex=threading.Lock()
dnsRepMutex=threading.Lock()

connectedUsers={}

keys={}

ttp=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def dnsConn(dns):
    global dnsBuff, dnsReply, dnsBuffMutex, dnsRepMutex
    while True:
        dnsBuffMutex.acquire()
        dnsRepMutex.acquire()
        if dnsBuff!='':
            local=dnsBuff
            dns.send(local.encode())
            dnsReply=dns.recv(1024).decode()
            dnsBuff=''
        dnsRepMutex.release()
        dnsBuffMutex.release()
            
def chatSend(sock, name):
    global connectedUsers
    while True:
        connectedUsers[name]['mutex'].acquire()
        if connectedUsers[name]['buffer']!='':

            splitKey=connectedUsers[name]['key'].split(',')
            splitKey[0]=int(splitKey[0])
            splitKey[1]=int(splitKey[1])
            
            sock.send(encryptString(connectedUsers[name]['buffer'], splitKey).encode())
            connectedUsers[name]['buffer']=''
        connectedUsers[name]['mutex'].release()
        

def chatRecv(sock, name):
    global connectedUsers, keys
    while True:
        data=sock.recv(65536).decode()

        data=decryptString(data, keys['priv'])

        print(f"<< {name} >> {data}")

def handleRequestedConnection(name):
    global connectedUsers
    ttp.send(f"check {name}".encode())
    connectedUsers[name]['key']=ttp.recv(65536).decode()
    newPerson=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newPerson.connect((connectedUsers[name]['addr'], connectedUsers[name]['port']))
    threading.Thread(target=chatSend, args=(newPerson, name,)).start()
    threading.Thread(target=chatRecv, args=(newPerson, name,)).start()
    while True:
        continue

def handleNewConnection(conn, port):
    global connectedUsers
    name=conn.recv(1024).decode()
    newPerson=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newPerson.bind(("0.0.0.0", port))
    conn.send(f"{socket.gethostbyname(socket.gethostname())} {port}".encode())
    conn.close()
    connectedUsers[name]={}
    connectedUsers[name]['addr']="0.0.0.0"
    connectedUsers[name]['port']=port
    connectedUsers[name]['buffer']=''
    connectedUsers[name]['mutex']=threading.Lock()
    ttp.send(f"check {name}".encode())
    connectedUsers[name]['key']=ttp.recv(65536).decode()
    newPerson.listen(1)
    conn, addr=newPerson.accept()
    print(f"(!STATUS) Connection established with {name}")
    threading.Thread(target=chatSend, args=(conn, name,)).start()
    threading.Thread(target=chatRecv, args=(conn, name,)).start()
    while True:
        continue

def mainListener(port):
    ass=1
    listener=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("0.0.0.0", port))
    listener.listen(10)
    for i in range(10):
        conn, addr=listener.accept()
        threading.Thread(target=handleNewConnection, args=(conn, port+ass, )).start()
        ass+=1

def inputFunc(uname):
    global dnsBuff, dnsReply, dnsBuffMutex, dnsRepMutex, connectedUsers, keys
    while True:
        command=str(input())
        command=command.split(">")
        if command[-1]=='@DNS':
            dnsBuffMutex.acquire()
            dnsBuff=command[0]
            dnsBuffMutex.release()
            time.sleep(1)
            dnsRepMutex.acquire()
            local=dnsReply
            dnsRepMutex.release()
            if 'RST' in dnsReply:
                print(f"(!ERROR) User {command[0]} does not exist")
                continue

            local=local.split(" ")
            newReq=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newReq.connect((str(local[1]), int(local[2])))
            newReq.send(uname.encode())
            rep=newReq.recv(1024).decode()
            newReq.close()
            if rep!='RST':
                rep=rep.split(' ')
                print(f"(!STATUS) Connection established with {local[0]}")
                connectedUsers[local[0]]={}
                connectedUsers[local[0]]['addr']=rep[0]
                connectedUsers[local[0]]['port']=int(rep[1])
                connectedUsers[local[0]]['buffer']=''
                connectedUsers[local[0]]['mutex']=threading.Lock()
                threading.Thread(target=handleRequestedConnection, args=(local[0],)).start()
            else:
                print(f"(!ERROR) Connection failed to establish with {local[0]}")

        elif command[-1]=='@TTP':
            if command[0]=='new':
                keys=generateKeys(2048)
                ttp.send(f"new {keys['pub'][0]},{keys['pub'][1]}".encode())
                if ttp.recv(65536).decode()=="ACK":
                    print("(!STATUS) Keys successfully changed!")
            else:
                print("(!ERROR) No valid command specified :(")

        elif command[-1]=='':
            print("(!ERROR) You did not write anything")
        else:
            if command[-1] in connectedUsers:
                connectedUsers[command[-1]]['mutex'].acquire()
                connectedUsers[command[-1]]['buffer']=command[0]
                connectedUsers[command[-1]]['mutex'].release()
            else:
                print(f"(!ERROR) You are not connected to {command[-1]}")


''' main for each client '''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dns:
    dns.connect((str(sys.argv[1]), int(sys.argv[2])))
    ttp.connect((str(sys.argv[3]), int(sys.argv[4])))
    uname=str(input("Please enter your username: "))
    port=int(input("Please enter your port number: "))

    keys=generateKeys(2048)
    ttp.send(f"{uname} {keys['pub'][0]},{keys['pub'][1]}".encode())
    ttpAck=ttp.recv(65536).decode()
    if "ACK" not in ttpAck:
        print("(!ERROR) Failed to connect to secure communication service")

    dns.send(f"{uname} {port}".encode())
    data=dns.recv(1024).decode()
    if "ACK" in data:
        threading.Thread(target=mainListener, args=(port,)).start()
        threading.Thread(target=dnsConn, args=(dns,)).start()
        threading.Thread(target=inputFunc, args=(uname, )).start()
        while True:
            continue
    else:
        print("(!ERROR) Failed to connect to chat service")
        exit()