import socket
import threading
import time

"""TTP Server for key management"""

users={}

def handleUser(conn, addr):
    data=''
    with conn:
        data=conn.recv(65536)
        data=data.decode().split(' ')
        print(data)
        users[data[0]]=[data[1], []]
        conn.send(b'ACK')
    
        while True:
            req=conn.recv(65536)
            req=req.decode().split(' ')
            
            if req[0]=='new':
                print(req)
                users[data[0]][1].clear()
                users[data[0]][0]=req[1]
                conn.send(b'ACK')
            elif req[0]=='check':
                if req[1] not in users:
                    conn.send(b'RST')
                elif data[0] in users[req[1]][1]:
                    conn.send(b'NOC')
                else:
                    print(req)
                    users[req[1]][1].append(data[0])
                    conn.send(users[req[1]][0].encode())
                    
    del users[data[0]]


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 8054))
    s.listen(10)
    for i in range(10):
        conn, addr=s.accept()
        threading.Thread(target=handleUser, args=(conn, addr,)).start()
