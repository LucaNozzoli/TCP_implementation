import socket
import logging
from os import path
from configs.config import TCP_SERVER_PORT, TCP_SERVER_IP, SERVER_BUFFER_SIZE
from helpers.utils import generate_checksum
import _thread
import time


class Server:
    def __init__(self) -> None:
        logging.getLogger().setLevel(logging.INFO)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((TCP_SERVER_IP, TCP_SERVER_PORT))
        self.server_socket.listen(1)
        logging.info(
            f"Server up and listening to {TCP_SERVER_IP} on port {TCP_SERVER_PORT}"
        )


    def generate_blocks(self, file_name):
        with open(file_name, "rb") as f:
            while True:
                data = f.read(SERVER_BUFFER_SIZE)
                if not data:
                    break
                yield data

    def send_file(self, connection):
        content = connection.recv(SERVER_BUFFER_SIZE)
        message = content.decode()
        file_name = message.split('/')[1]

        if path.exists(file_name):
            file = open(file_name, 'r')
            file_content = file.read()
            checksum = generate_checksum(file_content)
            payload = f'{filename}/{str(len(file_content))}/{checksum}'
            connection.send(payload.encode('utf-8')

            for chunk in generate_blocks(file_name, SERVER_BUFFER_SIZE):
                chunk_check = chunk + ('/' + generate_checksum(chunk)).encode('utf-8')
                connection.send(chunk_check)

                while True:
                    content = connection.recv(SERVER_BUFFER_SIZE)
                    if content == b'ack':
                        logging.info('Chunk sent')
                        break

                    elif content == b'fix':
                        logginng.info('Fixing chunk')
                        connection.send(chunk_check)

                    else:
                        logging.info(f'error: {content}')

            connection.send(b'eof')
            logging.info('Message sent to client')

            return
        
        else:
            connection.send('File not found'.encode())
            logginf.info('File not found')

            return

    def chat(self, connection, address):
        connection.send(b'Chat mode ON')
        while True:
            timeout = 5
            start_time = time.time()
            while(time.time()-start_time) < timeout:
                content = connection.recv(SERVER_BUFFER_SIZE)
                if content:
                    message = content.decode().strip()
                    logging.info(f'Client ({address}) -> {message}')

                    if message.lower() = 'chat: exit':
                        connection.send('Chat mode closed')
                        return

                    continue_chat = input('Keep chat open? (y/n):').lower == 'y'
                    if continue_chat:
                        chat_message = input('Message: ')
                        server_message = f'Chat: {chat_message}')
                        connection.send(server_message.encode())
                    else:
                        server_message = f'Server offline')
                        connection.send(server_message.encode())
                        return

                    start_time = time.time()
                else:
                    time.sleep(0.4)

        if (time.time()-start_time) >= timeout:
            connection.send('Timeout. Closing connection')
            return

    def connection_handler(self, connection, address):
        while True:
            content = connection.recv(BUFFER_SIZE)
            if not content:
                break
            message = content.decode()
            if message.lower() == "exit":
                logging.info( f"Client closed connection")
                connection.send(b"Client closed connection")
                break
            elif message.lower() == "file":
                send_file(connection=connection, address=address)
                break
            elif message.lower() == "chat":
                chat(connection=connection, address=address)
                break
            else:
                logging.info(data.decode())
                logging.info ("Invalid command: closing connection")
                connection.send(b"Invalid command: closing connection")
                break

        connection.close()

        return True

    def run_server(self) -> None:

        while True:
            connection, address = self.server_socket.accept()
            client_threads.acquire()

            _thread.start_new_thread(connection_handling, (connection, address))
        
            client_threads.release()















