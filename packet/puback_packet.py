from util.encode import encode_int16
from util.scanner import Scanner


class PubackPacket:

    def __init__(self, packet_id):
        self._packet_id = packet_id

    @property
    def packet_id(self):
        return self._packet_id

    def to_bytes(self):
        byte_array = bytearray()
        # fixed header
        byte_array.append(0b01000000)
        byte_array.append(0b00000010)
        # variable header
        packet_id_bytes = encode_int16(self._packet_id)
        byte_array.extend(packet_id_bytes)
        return bytes(byte_array)

    @staticmethod
    def from_bytes(packet_bytes):
        scanner = Scanner(packet_bytes)
        # skip fixed header
        scanner.skip_bytes(2)
        packet_id = scanner.next_bytes(2)
        return PubackPacket(packet_id)
