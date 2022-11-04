import socket
import threading
import time

"""DNS Server for storing active user information"""

users={}

def handleUser(conn, addr):
    data=''
    with conn:
        data=conn.recv(1024)
        data=data.decode().split(' ')
        users[data[0]]=(addr[0], int(data[1]))
        conn.send(b'ACK')
    
        while True:
            req=conn.recv(1024)
            req=req.decode()
            req=req.strip()
            if req in users:
                conn.send(f"{req} {users[req][0]} {users[req][1]}".encode())
            else:
                conn.send(b"RST")

    del users[data[0]]


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("0.0.0.0", 8053))
    s.listen(10)
    for i in range(10):
        conn, addr=s.accept()
        threading.Thread(target=handleUser, args=(conn, addr,)).start()
