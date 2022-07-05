import socket
from datetime import datetime
from select import select
from threading import Thread

# This code is adapted from https://github.com/MayankFawkes/Python-Proxy-Server


class ProxyServer:
    port = 30678
    host = "0.0.0.0"
    backlog = 50
    domain_block = ["googlesyndication.com", "msn.com", "bing.com"]
    auth = b"HTTP/1.1 200 Connection Established\r\n\r\n"
    http_block = b'HTTP/1.1 200 OK\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nContent-Type: text/html\r\n ' \
                 b'Connection: close\r\n\r\n<html><head><title> HTTP ERROR</' \
                 b'title></head><body><p style="text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;' \
                 b'</p><p style="text-align: center;">&nbsp;</p><p style="text-align: center;" >&nbsp;</p><p style=' \
                 b'"text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;</p><p style="text-align: ' \
                 b'center;"><span><strong>**HTTP PAGES HAVE BEEN BLOCKED BY YOUR INTERNAL FILTER**</strong>' \
                 b'</span></p><p style="text-align: center;"><span><strong>**To disable this ' \
                 b'change settings in RProxy client**</strong></span></p></body></html>'
    block_response = b''
    http_requests = ["get", "head", "post", "put", "delete", "connect", "options", "trace", "patch"]

    def __init__(self, proxy: dict = None):
        self.proxy = proxy
        print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Proxy Server Running on "
              f"{socket.gethostbyname(socket.gethostname())}:{self.port}")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.backlog)
        except socket.error as message:
            print(f"Could not open socket: {message}")
            exit()

    def process(self, conn, client_addr):
        raw_req = conn.recv(2048)
        #print(client_addr)
        #print(raw_req)
        if raw_req:
            #header = requests_header(head=raw_req, client_addr=client_addr)
            #def requests_header(head: bytes, client_addr: tuple, data: dict = {}):
            data = {}
            try:
                first = raw_req.split(b'\r\n')[0].split(b' ')
                if first[1].find(b"http://") != -1:
                    print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {client_addr[0]} \t Request \t {first}")
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
                    print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {client_addr[0]} \t Request \t {first}")
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
                    # print(data)
            except:
                print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {client_addr[0]} \t Error \t {b' '.join(first)}")
                # print(head)
            if ".".join(header["domain"].split(".")[-2:]) not in self.domain_block:
                if header["REQUESTS_TYPE"].lower() in ["connect"]:
                    self._action(conn=conn, host=header["domain"], port=header["PORT"], data=raw_req, type_="connect")
                else:
                    self._action(conn=conn, host=header["domain"], data=raw_req)
            else:
                print(f"Blocked {header['domain']}")
                conn.send(self.block_response)
                conn.close()
        else:
            print("No Raw Request")

    def _action(self, conn: object, host: str, port: int = 80, data: bytes = b"", type_: str = None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self.proxy:
                s.connect((self.proxy["host"], self.proxy["port"]))
                s.send(data)
            else:
                s.connect((host, port))
                if not type_:
                    s.send(data)
                else:
                    conn.send(self.auth)
        except:
            print(f'[{datetime.now().strftime("%I:%M:%S %p")}] Internet is not connected or domain invalid')
        while True:
            try:
                triple = select([conn, s], [], [])[0]
                if not len(triple):
                    break
                if conn in triple:
                    data = conn.recv(8192)
                    #print(f'Client data {len(data)} bytes: {data[:50]}')
                    if not data:
                        break
                    s.send(data)
                if s in triple:
                    data = s.recv(8192)
                    #print(f'Remote data {len(data)} bytes: {data[:50]}')
                    if data.startswith(b"HTTP/1.1"):
                        conn.send(self.http_block)
                        break
                    if not data:
                        break
                    conn.send(data)
            except:
                conn.close()
                s.close()

    def start(self):
        while True:
            s = Thread(target=self.process, args=(self.sock.accept()), )
            s.start()

    def __repr__(self):
        return f'<{self.__class__.__name__}.{self.__class__.__module__}' \
               f' host={self.host}, port={self.port} at {hex(id(self))}>'

    def __str__(self):
        return f'<{self.__class__.__name__}.{self.__class__.__module__}' \
               f' host={self.host}, port={self.port} at {hex(id(self))}>'

    @staticmethod
    def log(msg):
        with open("ProxyServer.logs", "a") as file:
            file.write(f'{msg}\n')


if __name__ == '__main__':
    ProxyServer(proxy={}).start()
