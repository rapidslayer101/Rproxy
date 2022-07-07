import socket
from datetime import datetime
from select import select
from threading import Thread

# todo possible errors with teams and microsoft security updates


class Threads:
    def __init__(self):
        self.threads_running = 0

    def new_thread(self):
        self.threads_running += 1
        return self.threads_running

    def remove_thread(self):
        self.threads_running -= 1


proxy = []  # the address of the external proxy server
proxy = ["127.0.0.1", 30677]
#proxy = ["192.168.1.231", 30677]
local_port = 30678
max_req = 50
domain_blocks = ["googlesyndication.com", "msn.com", "bing.com"]
http_block = b'HTTP/1.1 200 OK\r\nPragma: no-cache\r\nCache-Control: no-cache\r\nContent-Type: text/html\r\n ' \
             b'Connection: close\r\n\r\n<html><head><title> HTTP ERROR</' \
             b'title></head><body><p style="text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;' \
             b'</p><p style="text-align: center;">&nbsp;</p><p style="text-align: center;" >&nbsp;</p><p style=' \
             b'"text-align: center;">&nbsp;</p><p style="text-align: center;">&nbsp;</p><p style="text-align: ' \
             b'center;"><span><strong>**UNSECURE HTTP PAGES HAVE BEEN BLOCKED BY YOUR INTERNAL FILTER**</strong>' \
             b'</span></pp><p style="text-align: center;"><span><strong>**To disable this ' \
             b'change settings in RProxy client**</strong></span></p></body></html>'
block_response = b''  # todo https blocks page
http_requests = ["get", "head", "post", "put", "delete", "connect", "options", "trace", "patch"]

print(f"[{datetime.now().strftime('%I:%M:%S %p')}] Internal Proxy Running on "
      f"{socket.gethostbyname(socket.gethostname())}:{local_port}")
try:
    internal_firewall = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    internal_firewall.bind(("0.0.0.0", local_port))
    internal_firewall.listen(max_req)
except socket.error as socket_error:
    print(f"Could not open socket: {socket_error}")
    exit()


def process_req(local_connection, client_addr):
    raw_req = local_connection.recv(2048)
    connect = None
    if raw_req:
        header = {}
        try:
            first = raw_req.split(b'\r\n')[0].split(b' ')
            if first[1].find(b"http://") != -1:
                header["REQUESTS_TYPE"] = first[0].decode()
                header["PROTO"], other = first[1].split(b"://")
                domain_proto = other.split(b"/")[0]
                header["LOC_PARAMS"] = "/" + b"/".join(other.split(b"/")[1:]).decode()
                if domain_proto.find(b":") != -1:
                    domain = domain_proto.split(b":")[0].decode()
                    PORT = domain_proto.split(b":")[1].decode()
                else:
                    domain = domain_proto.decode()
                    PORT = 80
                header["domain"] = domain
                header["PORT"] = PORT
                return header
            else:
                header["PORT"] = 443
                header["REQUESTS_TYPE"] = first[0].decode()
                domain_proto = first[1].split(b"/")[0]
                header["domain"] = domain_proto.decode()
                header["LOC_PARAMS"] = "/" + b"/".join(first[1].split(b"/")[1:]).decode()
                if domain_proto.find(b":") != -1:
                    domain = domain_proto.split(b":")[0]
                    PORT = domain_proto.split(b":")[1]
                else:
                    domain = domain_proto
                    PORT = 80
                header["domain"] = domain.decode()
                if PORT:
                    header["PORT"] = int(PORT.decode())
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {threads.new_thread()} Threads -- \t Request \t {first}")
        except:
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {threads.new_thread()} Threads -- \t Error \t {first}")
        if ".".join(header["domain"].split(".")[-2:]) not in domain_blocks:
            if header["REQUESTS_TYPE"].lower() in ["connect"]:
                connect = 2
            else:
                connect = 1
        else:
            print(f"Blocked {header['domain']}")
    else:
        print("No Raw Request")

    if connect:
        try:
            if proxy:
                proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                proxy_sock.connect((proxy[0], proxy[1]))
                if connect == 1:
                    req_send = f"1{raw_req}🱫{header['domain']}🱫{header['PORT']}"
                    proxy_sock.send(req_send.encode())
                else:
                    req_send = f"{header['domain']}🱫{header['PORT']}"
                    proxy_sock.send(req_send.encode())
                    local_connection.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                while True:
                    try:
                        # todo proxy error for detecting which direction to send
                        # todo suggested fix by checking local_connection and destination connection
                        # then send the not null response
                        r_local_sock = select([local_connection], [], [])[0]
                        if not len(r_local_sock):
                            print("QUIT SOCKS LOOP -L")
                            proxy_sock.send(b"")
                        if local_connection in r_local_sock:
                            print("LOCAL RSOCK -S")
                            proxy_sock.send(b"LOCAL")
                        else:
                            print("LOCAL RSOCK -R")
                            proxy_sock.send(b"DESTIN")
                        r_destin_sock = proxy_sock.recv(8192)
                        if r_destin_sock == b"":
                            print("QUIT SOCKS LOOP -D")
                        if r_destin_sock == b"LOCAL":
                            print("LOCAL TRIP1")
                            print(r_local_sock, "LOCAL")
                            input()
                            client_data = local_connection.recv(8192)
                            if not client_data:
                                break
                            proxy_sock.send(client_data)
                        else:
                            if r_destin_sock == b"DESTIN":
                                print("DESTIN TRIP1")
                                print(r_local_sock, "DESTIN")
                                input()
                                proxy_sock.send(b"DESTIN")
                                remote_data = proxy_sock.recv(8192)
                                if remote_data.startswith(b"HTTP/1.1"):
                                    local_connection.send(http_block)
                                    break
                                if not remote_data:
                                    break
                                local_connection.send(remote_data)
                            else:
                                print("BROKE")
                                break
                    except Exception as e:
                        print(f"Error: {e}")
                        break
            else:
                destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                destination.connect((header["domain"], header["PORT"]))
                if connect == 1:
                    destination.send(raw_req)
                else:
                    local_connection.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                while True:
                    try:
                        read_socket = select([local_connection, destination], [], [])[0]
                        if not len(read_socket):
                            break
                        if local_connection in read_socket:
                            print("INT LOCAL")
                            client_data = local_connection.recv(8192)
                            if not client_data:
                                break
                            destination.send(client_data)
                        else:
                            if destination in read_socket:
                                print("INT DESTIN")
                                remote_data = destination.recv(8192)
                                if remote_data.startswith(b"HTTP/1.1"):
                                    local_connection.send(http_block)
                                    break
                                if not remote_data:
                                    break
                                local_connection.send(remote_data)
                            else:
                                break
                    except Exception as e:
                        print(f"Error: {e}")
                        break
        except:
            print(f'[{datetime.now().strftime("%I:%M:%S %p")}] Internet is not connected or domain invalid')
    if proxy:
        proxy_sock.close()
    else:
        destination.close()
    local_connection.close()
    threads.remove_thread()


if __name__ == '__main__':
    threads = Threads()
    while True:
        Thread(target=process_req, args=(internal_firewall.accept()), ).start()
