import socket
import logging
from random import randint

from configs.config import (
    TCP_CLIENT_PORT,
    TCP_CLIENT_IP,
    CLIENT_BUFFER_SIZE,
    DEFAULT_CLIENT_REQUEST,
)
from helpers.utils import verify_checksum


class Client:
    def __init__(self) -> None:
        logging.getLogger().setLevel(logging.INFO)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((TCP_CLIENT_IP, TCP_CLIENT_PORT))
        logging.info(
            f"client up and ready from {TCP_CLIENT_IP} on port {TCP_CLIENT_PORT}"
        )

    def generate_request(self, request_type, file_name) -> str:

        payload = (f"{request_type}/{file_name}")
        return payload

    def request_file(self):
        
        file_name = input('Insert desired filename:\n')

        payload = self.generate_request(
                request_type=DEFAULT_CLIENT_REQUEST, file_name=file_name
        )
        self.client_socket.send(payload.encode())

        try:
            first_req = True
            feedback = self.client_socket.recv(CLIENT_BUFFER_SIZE).decode('utf-8')
            logging.info(f'received data: {feedback}')
            received_filename = file_name.replace('.txt', '_received.txt')

            with open(received_filename, 'wb') as file:
                last_packet = b''
                while True:
                    if(last_packet and not last_packet.startswith(b"fix")) or first_req:
                        data = self.client_socket.recv(CLIENT_BUFFER_SIZE)
                        first_req = False
                    else:
                        self.client_socket.send(b'fix')
                        data = self.client_socket.recv(CLIENT_BUFFER_SIZE)
                    
                    if data == b'eof':
                        logging.info('file received')
                        return

                    message  = data.decode('utf-8').split('/')
                    print(message)
                    content  = message[0].encode('utf-8')
                    checksum = message[1]

                    if verify_checksum(content, checksum):
                        file.write(content)
                        logging.info('chunk received and checked')
                        self.client_socket.send(b'ack')
                        last_packet = content
                    else:
                        logging.info('packet check failed. retransmitting')
                        last_packet = b'fix'
                        self.client_socket.send(b'fix')

        except self.client_socket.timeout:
            logging.info('Conn timeout')
            self.client_socket.close()
            return

        self.client_socket.close()

    def chat(self):
        content = self.client_socket.recv(CLIENT_BUFFER_SIZE)
        logging.info(content.decode())
        payload = input('Insert payload:')
        message = f'Sending -> {payload}'
        self.client_socket.send(message.encode())
        while True:
            try:
                content = self.client_socket.recv(CLIENT_BUFFER_SIZE)
                if not content:
                    logging.info('No response from server')
                    break
                elif content == (b'Server offline'):
                    logging.info('Server offline')
                    break
                elif content == (b'Chat mode closed'):
                    logging.info('Chat mode closed')
                    break
                logging.info(content.decode())
                payload = input('Insert payload:')
                message = f'Sending -> {payload}'
                self.client_socket.send(message.encode())
            except ConnectionError:
                logging.info('Connection lost')
                break




    def startup_selections(self):
        logging.info(
            """Select desired mode by choosing one of the following numbers
    arquivo: 1,
    chat: 2,
    close: 0""",
        )
        file_option = input()

        self.client_socket.send(file_option.encode('utf-8'))

        if file_option ==  "1": 
            self.request_file()
        elif file_option == "2":
            self.chat()
        else:
            self.client_socket.close()


    def run_client(self) -> None:

        self.startup_selections()

        













