"""
Minimal SSL/TLS termination proxy

Run in background:
    python ssloxy.py start > /dev/null 2>&1 &
Stop:
    python ssloxy.py stop
"""

import sys
import argparse

import ssl
import socket

from threading import Thread

import logging

logging.basicConfig(filename='./ssloxy.log', level=logging.INFO, filemode='a',
                    format='%(threadName)s  %(asctime)s : %(levelname)s : %(message)s')


TEST_ENV        = False                  # самодельные сертификаты

HOST, PORT      = "localhost", 8443     # openssl s_client -connect localhost:8443 / ncat --ssl localhost 8443
BHOST, BPORT    = "localhost", 8000     # ncat -lk localhost 8000

SHUTDOWN        = b"SHUTDOWN"           # команда выключения сервера
FINISH          = b"FINISH"             # конец сессии
BUFFER          = 1024                  # размер буфера



def in_stream(client, backend, data):
    
    backend.send(data)
    logging.debug(f"-> backend: {data}")

    while data:
        try:
            data = client.recv(BUFFER)
            backend.send(data)
            logging.debug(f"-> backend: {data}")
        except socket.error:
            break
        if FINISH in data.split(b'\n'):
            break
    
    logging.info("Session finished")

def out_stream(client, backend):
    try:
        data = backend.recv(BUFFER)
        client.send(data)
        logging.debug(f"-> client: {data}")
    except socket.error:
        data = False

    while data:
        try:
            data = backend.recv(BUFFER)
            client.send(data)
            logging.debug(f"-> client: {data}")
        except socket.error:
            break

def main_thread():
    """"""

    logging.info("Main thread")

    if TEST_ENV:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('./cert/server.crt', './cert/server.key')
    else:
        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:    
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.listen(65536)
        
        with context.wrap_socket(sock, server_side=True) as ssock:

            while True:
                sconn, addr = ssock.accept()

                logging.info(f"{addr} connected")

                data = sconn.recv(len(SHUTDOWN))
                if data == SHUTDOWN:
                    logging.info(f"Recieved {str(SHUTDOWN)}")
                    break
                
                backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                backend.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    backend.connect( (BHOST, BPORT) )
                    logging.info(f"Connected to backend")
                except ConnectionRefusedError:
                    logging.info(f"Backend refused connection")
                    sconn.shutdown(socket.SHUT_RDWR)
                    sconn.close()
                    continue

                reader = Thread(target = in_stream, args = ( sconn, backend, data ), daemon=True)
                writer = Thread(target = out_stream, args = ( sconn, backend ), daemon=True )

                reader.start()
                writer.start()

            logging.info("Server stopped")


def start():
    server_thread = Thread(target = main_thread)
    server_thread.start()

    print("Server loop running in thread:", server_thread.name)


def stop():
    logging.info("Stopping")

    if TEST_ENV:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False      # подлинность домена не проверяется
        context.verify_mode = ssl.CERT_NONE # цепочка сертификатов не проверяется
    else:
        context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    
    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
           
            ssock.send(SHUTDOWN)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simple SSL/TLS termination proxy to single backend non-SSL service')
    
    parser.add_argument('command', type=str, help='start|stop')
    parser.add_argument('-a', '--addr', type=str, default=HOST, help=f"SSL proxy host (dafault: {HOST})")
    parser.add_argument('-p', '--port', type=int, default=PORT, help=f"SSL proxy port (dafault: {PORT})")
    parser.add_argument('-b', '--baddr', type=str, default=BHOST, help=f"Backend host (dafault: {BHOST})")
    parser.add_argument('-s', '--bport', type=int, default=BPORT, help=f"Backend port (dafault: {BPORT})")
    parser.add_argument('-t', '--test', action='store_true', help=f"Use self-signed certificate from ./cert")


    args = parser.parse_args()
    
    HOST = args.addr
    PORT = args.port
    BHOST = args.baddr
    BPORT = args.bport
    TEST_ENV = args.test
    
    if args.command == "start":
        try:
            start()
            print(f"SSL/TLS termination proxy from '{HOST}:{PORT}' to '{BHOST}:{BPORT}' started")
            print(f"Use '<Ctrl-C>' to stop")

        except OSError:
            print("The address is already in use")
            sys.exit(1)
        
    if args.command == "stop":
        stop()
