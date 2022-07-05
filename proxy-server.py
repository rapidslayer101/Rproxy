import socket
from datetime import datetime
from select import select
from threading import Thread

# todo make function


class Threads:
    def __init__(self):
        self.threads_running = 0

    def new_thread(self):
        self.threads_running += 1
        return self.threads_running

    def remove_thread(self):
        self.threads_running -= 1


proxy = []  # the address of the external proxy server
local_port = 30677
max_req = 50
domain_blocks = ["googlesyndication.com", "msn.com", "bing.com"]
http_requests = ["get", "head", "post", "put", "delete", "connect", "options", "trace", "patch"]

print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Internal Proxy Running on "
      f"{socket.gethostbyname(socket.gethostname())}:{local_port}")
try:
    internal_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    internal_proxy.bind((f"{socket.gethostbyname(socket.gethostname())}", local_port))
    internal_proxy.listen(max_req)
except socket.error as socket_error:
    print(f"Could not open socket: {socket_error}")
    exit()


def process_req(local_connection, client_addr):
    raw_req, connect, host, port = local_connection.recv(2048).decode().split("🱫")
    print(host, port)
    destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        destination.connect((host, int(port)))
        if int(connect) == 1:
            destination.send(raw_req)
        else:
            local_connection.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        while True:
            try:
                triple = select([local_connection, destination], [], [])[0]
                if not len(triple):
                    print("break")
                    break
                print(local_connection)
                if local_connection in triple:
                    client_data = local_connection.recv(8192)
                    if not client_data:
                        break
                    destination.send(client_data)
                else:
                    if destination in triple:
                        remote_data = destination.recv(8192)
                        if not remote_data:
                            break
                        print(remote_data)
                        local_connection.send(remote_data)
                    else:
                        break
            except Exception as e:
                print(f"Error: {e}")
                break
    except:
        print(f'[{datetime.now().strftime("%I:%M:%S %p")}] Internet is not connected or domain invalid')
    destination.close()
    local_connection.close()
    threads.remove_thread()


if __name__ == '__main__':
    threads = Threads()
    while True:
        s = Thread(target=process_req, args=(internal_proxy.accept()), ).start()
