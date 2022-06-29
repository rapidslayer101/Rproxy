# connect to proxy server

import socket
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("63.32.41.221", 28422))
print("connected")
conn.send("https://google.com".encode())
data = conn.recv(1024)
print(data)
conn.close()
