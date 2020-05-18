import socket
import sys, time
import errno


IP = str(sys.argv[1])
PORT = int(sys.argv[2])

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = input("Username: ").encode('utf-8')
client_socket.send(username)
d = client_socket.recv(2048)
print(d.decode('utf-8'))
time.sleep(2)
d = client_socket.recv(2048)
print(d.decode('utf-8'))