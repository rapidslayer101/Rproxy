# connect to proxy server

import socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("172.", 80))
print("connected")
conn.send("https://google.com".encode())
data = conn.recv(1024)
print(data)
conn.close()
