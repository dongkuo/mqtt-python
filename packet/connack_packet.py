from util.scanner import Scanner


class ConnackPacket:
    """Connack Packet"""

    def __init__(self, sp: bool, return_code):
        self._sp = sp
        self._return_code = return_code

    @property
    def sp(self):
        return self._sp

    @property
    def return_code(self):
        return self._return_code

    @staticmethod
    def from_bytes(packet_bytes):
        scanner = Scanner(packet_bytes)
        scanner.mark()
        # 跳过前两个字节的固定头部
        scanner.skip_bytes(2)
        # 读取 Session Present Flag
        sp_value = scanner.skip_bits(7).next_bits(1)
        sp = True if sp_value == 1 else 0
        # 读取 Connect Return code
        return_code = scanner.next_bytes()
        return ConnackPacket(sp, return_code)

    def __str__(self):
        return 'ConnackPacket(sp = {}, return_code = {})'.format(self._sp, self._return_code)
