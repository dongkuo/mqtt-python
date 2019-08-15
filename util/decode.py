from util.scanner import Scanner


def decode_remaining_length(scanner: Scanner):
    first_byte = scanner.next_bytes()
    remaining_length = first_byte & 0x7F
    flag = first_byte & 0x80
    multiplier = 1
    while True:
        if not flag:
            return remaining_length
        next_byte = scanner.next_bytes()
        flag = next_byte & 0x80
        remaining_length += (next_byte & 0x7F) * multiplier


def skip_remaining_length_byte(scanner: Scanner):
    next_byte = scanner.next_bytes()
    flag = next_byte & 0x80
    while True:
        if not flag:
            return
        next_byte = scanner.next_bytes()
        flag = next_byte & 0x80
