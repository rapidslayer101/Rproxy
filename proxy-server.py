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
    #internal_proxy.bind((f"{socket.gethostbyname(socket.gethostname())}", local_port))
    internal_proxy.bind((f"0.0.0.0", local_port))
    internal_proxy.listen(max_req)
except socket.error as socket_error:
    print(f"Could not open socket: {socket_error}")
    exit()


def process_req(client, client_addr):
    raw_req, connect, host, port = client.recv(8192).decode().split("🱫")
    print(host, port)
    destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        destination.connect((host, int(port)))
        if int(connect) == 1:
            destination.send(raw_req)
        while True:
            try:
                triple = select([client, destination], [], [])[0]
                if not len(triple):
                    print("BROKE")
                    break
                if client in triple:
                    print("DIR1 LOCAL")
                    client.send(b"LOCAL")
                    client_data = client.recv(8192)
                    if not client_data:
                        break
                    destination.send(client_data)
                else:
                    if destination in triple:
                        print("DIR1 DESTIN")
                        client.send(b"DESTIN")
                        remote_data = destination.recv(8192)
                        if not remote_data:
                            break
                        print(remote_data)
                        client.send(remote_data)
                    else:
                        print("BROKE")
                        break
            except Exception as e:
                print(f"Error: {e}")
                break
    except:
        print(f'[{datetime.now().strftime("%I:%M:%S %p")}] Internet is not connected or domain invalid')
    destination.close()
    threads.remove_thread()
    print("ENDED")


if __name__ == '__main__':
    threads = Threads()
    while True:
        Thread(target=process_req, args=(internal_proxy.accept()), ).start()
