from util.scanner import Scanner


class SubackPacket:

    def __init__(self, packet_id, return_codes):
        self._packet_id = packet_id
        self._return_codes = return_codes

    @property
    def packet_id(self):
        return self._packet_id

    @property
    def return_codes(self):
        return self._return_codes

    @staticmethod
    def from_bytes(packet_bytes):
        scanner = Scanner(packet_bytes)
        # 跳过固定头部第1个字节
        scanner.skip_bytes(1)
        # Remaining Length
        remaining_length = scanner.next_bytes()
        # packet_id
        packet_id = scanner.next_bytes(2)
        # return code array
        return_codes = []
        for _ in range(remaining_length - 2):
            return_codes.append(scanner.next_bytes())
        return SubackPacket(packet_id, return_codes)

    def __str__(self):
        return 'SubackPacket(packet_id = {}, return_codes = {})'.format(self._packet_id, self._return_codes)
