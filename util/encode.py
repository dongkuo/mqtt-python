def encode_remaining_length(remaining_length):
    ba = bytearray()
    while remaining_length > 0:
        byte = remaining_length % 128
        remaining_length = remaining_length // 128
        if remaining_length > 0:
            # 说明还需要更多的字节去编码，因此将本字节的最高位置为1
            byte = byte | 128
        ba.append(byte)
    return bytes(ba)


def encode_string(string):
    ba = bytearray()
    if string:
        length = len(bytes(string, 'utf-8'))
        ba.extend(length.to_bytes(length=2, byteorder='big', signed=False))
        ba.extend(bytes(string, 'utf-8'))
    return bytes(ba)


def encode_int16(number: int):
    if number > 0xFFFF:
        raise ValueError('the number must less than or equal 65535')
    ba = bytearray()
    ba.append(number >> 8)
    ba.append(number & 0x00FF)
    return bytes(ba)
