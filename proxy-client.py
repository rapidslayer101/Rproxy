# connect to proxy server

import socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("127.0.0.1", 30678))
print("connected")
conn.send("https://google.com".encode())
data = conn.recv(1024)
print(data)
conn.close()
