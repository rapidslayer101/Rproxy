import socket
from datetime import datetime
from select import select
from threading import Thread

# This code is adapted from https://github.com/MayankFawkes/Python-Proxy-Server

# todo possible errors with teams and microsoft security updates


class Threads:
    def __init__(self):
        self.threads_running = 0

    def new_thread(self):
        self.threads_running += 1
        return self.threads_running

    def remove_thread(self):
        self.threads_running -= 1


proxy = []
#proxy = ["127.0.0.1", 30677]
internal_port = 30678
backlog = 50
domain_block = ["googlesyndication.com", "msn.com", "bing.com"]
auth = b"HTTP/1.1 200 Connection Established\r\n\r\n"
http_block = b'HTTP/1.1 200 OK\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nContent-Type: text/html\r\n ' \
             b'Connection: close\r\n\r\n<html><head><title> HTTP ERROR</' \
             b'title></head><body><p style="text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;' \
             b'</p><p style="text-align: center;">&nbsp;</p><p style="text-align: center;" >&nbsp;</p><p style=' \
             b'"text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;</p><p style="text-align: ' \
             b'center;"><span><strong>**HTTP PAGES HAVE BEEN BLOCKED BY YOUR INTERNAL FILTER**</strong>' \
             b'</span></pp><p style="text-align: center;"><span><strong>**To disable this ' \
             b'change settings in RProxy client**</strong></span></p></body></html>'
block_response = b''
http_requests = ["get", "head", "post", "put", "delete", "connect", "options", "trace", "patch"]

print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Internal Proxy Running on "
      f"{socket.gethostbyname(socket.gethostname())}:{internal_port}")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", internal_port))
    sock.listen(backlog)
except socket.error as message:
    print(f"Could not open socket: {message}")
    exit()


def process(conn, client_addr):
    raw_req = conn.recv(2048)
    #print(client_addr)
    #print(raw_req)
    if raw_req:
        data = {}
        try:
            first = raw_req.split(b'\r\n')[0].split(b' ')
            if first[1].find(b"http://") != -1:
                print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {threads.new_thread()} "
                      f"Threads -- {client_addr[0]} \t Request \t {first}")
                data["REQUESTS_TYPE"] = first[0].decode()
                data["PROTO"], other = first[1].split(b"://")
                domain_proto = other.split(b"/")[0]
                data["LOC_PARAMS"] = "/" + b"/".join(other.split(b"/")[1:]).decode()
                if domain_proto.find(b":") != -1:
                    domain = domain_proto.split(b":")[0].decode()
                    PORT = domain_proto.split(b":")[1].decode()
                else:
                    domain = domain_proto.decode()
                    PORT = 80
                data["domain"] = domain
                data["PORT"] = PORT
                return data
            else:
                print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {threads.new_thread()} "
                      f"Threads -- {client_addr[0]} \t Request \t {first}")
                data["PORT"] = 443
                data["REQUESTS_TYPE"] = first[0].decode()
                domain_proto = first[1].split(b"/")[0]
                data["domain"] = domain_proto.decode()
                data["LOC_PARAMS"] = "/" + b"/".join(first[1].split(b"/")[1:]).decode()
                if domain_proto.find(b":") != -1:
                    domain = domain_proto.split(b":")[0]
                    PORT = domain_proto.split(b":")[1]
                else:
                    domain = domain_proto
                    PORT = 80
                data["domain"] = domain.decode()
                if PORT:
                    data["PORT"] = int(PORT.decode())
                header = data
                #print(data)
        except:
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {threads.new_thread()} "
                  f"Threads -- {client_addr[0]} \t Error \t {b' '.join(first)}")
            # print(head)
        if ".".join(header["domain"].split(".")[-2:]) not in domain_block:
            if header["REQUESTS_TYPE"].lower() in ["connect"]:
                action(conn=conn, d_host=header["domain"], d_port=header["PORT"], data=raw_req, type_="connect")
            else:
                action(conn=conn, d_host=header["domain"], d_port=raw_req)
        else:
            print(f"Blocked {header['domain']}")
            conn.send(block_response)
            conn.close()
            threads.remove_thread()
    else:
        print("No Raw Request")


def action(conn, d_host, d_port, data, type_: str = None):
    destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if proxy:
            destination.connect((proxy[0], proxy[1]))
            destination.send(data)
        else:
            destination.connect((d_host, d_port))
            if not type_:
                destination.send(data)
            else:
                conn.send(auth)
    except:
        print(f'[{datetime.now().strftime("%I:%M:%S %p")}] Internet is not connected or domain invalid')
    while True:
        try:
            triple = select([conn, destination], [], [])[0]
            if not len(triple):
                print("break")
                break
            if conn in triple:
                data = conn.recv(8192)
                #print(f'Client data {len(data)} bytes: {data[:50]}')
                if not data:
                    break
                destination.send(data)
            else:
                if destination in triple:
                    data = destination.recv(8192)
                    #print(f'Remote data {len(data)} bytes: {data[:50]}')
                    if data.startswith(b"HTTP/1.1"):
                        conn.send(http_block)
                        break
                    if not data:
                        break
                    conn.send(data)
                else:
                    break
        except Exception as e:
            print(f"Error: {e}")
            break
    conn.close()
    destination.close()
    threads.remove_thread()


if __name__ == '__main__':
    threads = Threads()
    while True:
        s = Thread(target=process, args=(sock.accept()), ).start()
