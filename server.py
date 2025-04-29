import socket

from file import serializer
from input_command import InputCommand
from threader import thread_function


def read_input_command(input_line):
    commands = input_line.split(", ")
    command = InputCommand()
    for index, i in enumerate(commands):
        if index == 0:
            command.command_name = i
        elif index == 1:
            command.file_name = i
        else:
            i = i.strip('\n')
            command.arguments.append(i)
    return command


def client_thread(connection: socket, input_structure: list):
    username = connection.recv(1024).decode('utf-8')
    connection.sendall(str.encode('Hi {},'.format(username)))

    while True:
        received_data = connection.recv(1024)
        decoded_data = received_data.decode('utf-8')
        command = read_input_command(decoded_data)
        if not received_data:
            break
        if decoded_data == 'exit':
            print(f'Client named: {username} has closed the connection')
            serializer(input_structure)
            break
        input_structure = thread_function([command], input_structure, connection)

    connection.close()
