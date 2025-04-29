import os
import socket

from file import deserializer
from server import client_thread
from threader import Threader

file_structure = []
HOST = ''
PORT_NO = 95


def main(input_structure):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT_NO))
    except socket.error as err:
        print(str(err))
    print('Server is running\nListening for connections...')
    server_socket.listen(5)
    if os.path.exists('file-structure.img'):
        input_structure = deserializer()
    while True:
        connection, address = server_socket.accept()
        print('Connected to IP address ' + address[0] + ' at port number ' + str(address[1]))
        thread = Threader(target=client_thread, args=(connection, input_structure))
        thread.start()


if __name__ == "__main__":
    main(file_structure)
