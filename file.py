import pickle

MEMORY_SIZE = 5000


class File:
    def __init__(self, file_name: str, file_data: str):
        self.file_name = file_name
        self.data = file_data
        self.is_last = True


def serializer(input_structure: list) -> None:
    with open('file-structure.img', 'wb') as file:
        pickle.dump(input_structure, file)


def deserializer() -> list:
    with open('file-structure.img', 'rb') as file:
        input_structure = pickle.load(file)
        return input_structure


def list_converter(input_string: str) -> list:
    return [input_string[i:i + 32] for i in range(0, len(input_string), 32)]


def file_existence_checker(input_name: str, input_structure: list) -> bool:
    for index, i in enumerate(input_structure):
        if i.file_name == input_name:
            return True
    return False


def get_initial_index(input_name: str, input_structure: list) -> int:
    for index, i in enumerate(input_structure):
        if i.file_name == input_name:
            return index
    return -1


def get_last_index(input_name: str, input_structure: list) -> int:
    for index, i in enumerate(input_structure):
        if i.file_name == input_name and i.is_last:
            return index
    return -1


def get_structure_size(input_structure: list) -> int:
    total_bytes = 0
    for i in input_structure:
        total_bytes += len(i.file_name)
        total_bytes += len(i.data)
    return total_bytes


def rewriter(initial_index: int, ending_index: int, input_name: str, input_data: str, input_structure: list,
             output_file, is_truncate=False, truncate_index=0, ) -> list:
    next_chunks = input_structure.copy()
    del input_structure[initial_index:len(input_structure)]
    del next_chunks[0:ending_index + 1]
    create(input_name, input_structure)
    if is_truncate:
        write(input_name, input_data[0:truncate_index], input_structure, output_file)
    else:
        write(input_name, input_data, input_structure, output_file)
    input_structure.extend(next_chunks)
    return input_structure


def create(input_name: str, input_structure: list) -> str:
    if len(input_name) + get_structure_size(input_structure) >= MEMORY_SIZE:
        return 'Insufficient storage!'
    if len(input_name) > 32:
        return 'File name is too big'
    if file_existence_checker(input_name, input_structure):
        return f'{input_name} already exists'
    else:
        if input_name is not None and input_name != '':
            input_structure.append(File(input_name, ''))
            return f'File {input_name} created successfully'
        else:
            return 'File name cannot be empty'


def read(input_name: str, input_structure: list) -> str:
    if file_existence_checker(input_name, input_structure):
        output_string = ''
        for i in input_structure:
            if i.file_name == input_name:
                output_string += i.data
        if output_string == '':
            return ''
        else:
            return output_string
    else:
        return 'No file Found'


def read_from(input_name: str, starting_index: int, reading_size: int, input_structure: list) -> str:
    output_string = read(input_name, input_structure)
    if len(output_string) == 0:
        return 'No content found'
    elif (starting_index + reading_size) > len(output_string):
        return 'Provided size is greater than total file content.'
    else:
        return output_string[starting_index:starting_index + reading_size]


def write(input_name: str, input_data: str, input_structure: list, connection_pointer) -> list:
    file_exists = False
    for f_index, i in enumerate(input_structure):
        if i.file_name == input_name and i.is_last:
            file_exists = True
            i.is_last = False
            if (len(input_data) + (len(list_converter(input_data)) * len(input_name)) + get_structure_size(
                    input_structure)) > MEMORY_SIZE:
                connection_pointer.sendall(str.encode('Insufficient storage!'))
                return input_structure

            # If file has no content
            if len(i.data) == 0:
                if len(input_data) <= 32:
                    input_structure[f_index] = File(input_name, input_data)
                    connection_pointer.sendall(str.encode('File written successfully'))
                    return input_structure
                data_list = list_converter(input_data)
                for index, files in enumerate(data_list):
                    f = File(input_name, files)
                    f.is_last = False
                    if index == 0:
                        input_structure[f_index] = f
                    elif index + 1 == len(data_list):
                        f.is_last = True
                        input_structure.append(f)
                    else:
                        input_structure.append(f)
                connection_pointer.sendall(str.encode('File written successfully'))
                return input_structure

            # If file already has content in it
            elif len(i.data) <= 32:
                diff = 32 - len(i.data)
                i.data += input_data[0:diff]
                if len(input_data[diff:len(input_data)]) == 0:
                    i.is_last = True
                else:
                    i.is_last = False
                data_list = list_converter(input_data[diff:len(input_data)])
                for index, files in enumerate(data_list):
                    f = File(input_name, files)
                    f.is_last = False
                    if index + 1 == len(data_list):
                        f.is_last = True
                    input_structure.append(f)
                connection_pointer.sendall(str.encode('File written successfully'))
                return input_structure

            # If file is not last in the list
            elif f_index + 1 != len(input_structure):
                i.is_last = True
                files_after_required_file = []
                for to_delete_index in range(f_index + 1, len(input_structure)):
                    files_after_required_file.append(input_structure.pop(f_index + 1))
                write(input_name, input_data, input_structure, connection_pointer)
                input_structure.extend(files_after_required_file)
                connection_pointer.sendall(str.encode('File written successfully'))
                return input_structure

    if not file_exists:
        connection_pointer.sendall(str.encode('File not found'))
        return input_structure


def write_at(input_name: str, write_at_index: int, input_data: str, input_structure: list, connection_pointer) -> list:
    starting_index = get_initial_index(input_name, input_structure)
    last_index = get_last_index(input_name, input_structure)
    is_file_exists = file_existence_checker(input_name, input_structure)
    read_data = read(input_name, input_structure)

    if len(read_data) == 0:
        connection_pointer.sendall(str.encode('\nCannot write at index in empty file!\n'))
        return input_structure
    read_data = read_data[0:write_at_index] + input_data + read_data[write_at_index:len(read_data)]
    if is_file_exists:
        if (len(input_data) + (len(list_converter(input_data)) * len(input_name)) + get_structure_size(
                input_structure)) > MEMORY_SIZE:
            connection_pointer.sendall(str.encode('Insufficient storage!'))
            return input_structure
        return rewriter(starting_index, last_index, input_name, read_data, input_structure, connection_pointer)
    else:
        connection_pointer.sendall(str.encode('\nFile not found\n'))
        return input_structure


def delete(input_name: str, input_structure: list) -> str:
    start_index = get_initial_index(input_name, input_structure)
    last_index = get_last_index(input_name, input_structure)
    if file_existence_checker(input_name, input_structure):
        del input_structure[start_index:last_index + 1]
        return 'File deleted successfully'
    return 'No File Found'


def truncate(input_name: str, truncate_index: int, input_structure: list, connection_pointer) -> list:
    starting_index = get_initial_index(input_name, input_structure)
    last_index = get_last_index(input_name, input_structure)
    is_file_exists = file_existence_checker(input_name, input_structure)
    read_data = read(input_name, input_structure)

    if len(read_data) < truncate_index:
        connection_pointer.sendall(str.encode('Given index is greater than total file size'))
        return input_structure
    if is_file_exists:
        return rewriter(starting_index, last_index, input_name, read_data, input_structure, connection_pointer, True,
                        truncate_index)
    else:
        connection_pointer.sendall(str.encode('File not found'))
        return input_structure


def move_within_file(input_name: str, initial_index: int, ending_index: int, data_size: int,
                     input_structure: list, connection_pointer) -> list:
    starting_index = get_initial_index(input_name, input_structure)
    last_index = get_last_index(input_name, input_structure)
    file_exists = file_existence_checker(input_name, input_structure)
    read_data = read(input_name, input_structure)
    data_to_move = read_data[initial_index:initial_index + data_size]

    if initial_index + data_size < ending_index and ending_index > initial_index:
        read_data = read_data[0:initial_index] + \
                    read_data[initial_index + data_size:ending_index] + \
                    data_to_move + read_data[ending_index:len(read_data)]

    elif initial_index > ending_index:
        read_data = read_data[0:ending_index] + \
                    data_to_move + \
                    read_data[ending_index:initial_index] + \
                    read_data[initial_index + data_size:len(read_data)]
    else:
        connection_pointer.sendall(str.encode('Invalid parameters!'))
        return input_structure
    if file_exists:
        return rewriter(starting_index, last_index, input_name, read_data, input_structure, connection_pointer)
    else:
        connection_pointer.sendall(str.encode('File not found'))
        return input_structure


def rename(existing_file_name: str, new_file_name: str, input_structure: list) -> str:
    file_exists = file_existence_checker(existing_file_name, input_structure)
    new_file_name_exists = file_existence_checker(new_file_name, input_structure)
    if new_file_name_exists:
        return 'File name already exists'
    else:
        if (len(new_file_name) + get_structure_size(input_structure)) > MEMORY_SIZE:
            return 'Insufficient storage!'
        if file_exists:
            for i in input_structure:
                if i.file_name == existing_file_name:
                    i.file_name = new_file_name
            return 'File renamed successfully'
        else:
            return 'File does not exist'


def memory_map_creator(input_structure) -> dict:
    memory_map = {}
    for index, i in enumerate(input_structure):
        if i.file_name not in memory_map:
            memory_map[i.file_name] = {
                'name': i.file_name,
                'chunks': [index],
                'bytes': len(read(i.file_name, input_structure)) + len(i.file_name)
            }
        else:
            chunk_list = memory_map[i.file_name]['chunks']
            chunk_list.append(index)
            memory_map[i.file_name] = {
                'name': i.file_name,
                'chunks': chunk_list,
                'bytes': memory_map[i.file_name]['bytes'] + len(i.file_name)
            }

    return memory_map


def print_memory_map(input_structure: list, connection_pointer) -> None:
    memory_map = memory_map_creator(input_structure)
    data_to_send = "\n********** Memory Map View **********\n\n" + \
                   "{:<20} {:<20} {:<20}\n".format('File Name', 'Chunk Number', 'Total Bytes')
    for i in memory_map:
        chunks = [str(i) for i in memory_map[i].get('chunks')]
        output_map = "{:<20} {:<20} {:<20}\n".format(memory_map[i].get('name'), ', '.join(chunks),
                                                     memory_map[i].get('bytes')),
        data_to_send += ''.join(output_map)
    connection_pointer.sendall(str.encode(data_to_send))
