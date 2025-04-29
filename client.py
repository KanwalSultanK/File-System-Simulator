import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 95


def print_user_interface():
    print('\n********** File System Simulator **********\n\n' +
          'create,\t\t\t\t\t<filename>\n' +
          'read,\t\t\t\t\t<filename>\n' +
          'read_from,\t\t\t\t<filename>, <starting-index>, <characters_to_read>\n' +
          'write,\t\t\t\t\t<filename>, <input-data>\n' +
          'write_at,\t\t\t\t<filename>, <index>, <input-data>\n' +
          'move,\t\t\t\t\t<filename>, <from-index>, <to-index>, <size>\n' +
          'delete,\t\t\t\t\t<filename>\n' +
          'truncate,\t\t\t\t<filename>, <truncate-index>\n' +
          'rename,\t\t\t\t\t<previous-filename>, <new-filename>\n' +
          'get_directory_size\n' +
          'show\n' +
          'exit\n\n')


def main():
    input_command = ''
    host_address = str(input('Enter the IP of server: '))
    print('Connecting with Server...')

    try:
        client_socket.connect((host_address, PORT))
    except socket.error as err:
        print(str(err))
        exit(0)
    print('Connection Established')
    username = str(input('Enter your name: '))
    client_socket.sendall(str.encode(username))
    # Print the welcome message
    print(client_socket.recv(1024).decode('utf-8'))
    print_user_interface()

    while input_command != 'exit':
        input_command = input('Enter the file command: ')
        client_socket.send(str.encode(input_command))
        server_response = client_socket.recv(4096).decode('utf-8')
        if server_response == 'executing':
            print("Current File is under process so cannot be accessed")
            print(client_socket.recv(4096).decode('utf-8'))
        else:
            print(server_response)
    client_socket.close()


if __name__ == '__main__':
    main()
