from functools import reduce


class Scanner:
    """A scanner for reading bytes"""

    def __init__(self, data: bytes, offset_byte=0, offset_bit=0):
        self.data = data
        self._offset_byte = offset_byte
        self._offset_bit = offset_bit
        self._marked_offset_byte = 0
        self._marked_offset_bit = 0

    def skip_bits(self, n=1):
        self._check_bits(n)
        self._move_bits(n)
        return self

    def next_bits(self, n=1):
        """读取 n 位"""
        self._check_bits(n)
        result = self.data[self._offset_byte] >> (8 - self._offset_bit - n)
        result = result & ((1 << n) - 1)
        self._move_bits(n)
        return result

    def skip_bytes(self, n=1):
        """跳过 n 个字节"""
        self._check_bytes(n)
        self._move_bytes(n)
        return self

    def next_bytes(self, n=1, convert=True, move=True):
        """读取 n 个字节, n从1开始计数"""
        self._check_bytes(n)
        result = self.data[self._offset_byte: self._offset_byte + n]
        if move:
            self._move_bytes(n)
        if convert:
            result = int.from_bytes(result, 'big')
        return result

    def next_bytes_until(self, stop, convert=True):
        if not self._offset_bit == 0:
            raise RuntimeError('当前字节不完整，请先读取完当前字节的所有位')
        end = self._offset_byte
        while not stop(self.data[end], end - self._offset_byte):
            end += 1
        result = self.data[self._offset_byte: end]
        self._offset_byte = end
        if convert:
            if result:
                result = reduce(lambda x, y: y if (x == '.') else x + y,
                                map(lambda x: chr(x) if (31 < x < 127) else '.', result))
            else:
                result = ''
        return result

    def remains_bytes(self):
        if not self._offset_bit == 0:
            raise RuntimeError('当前字节不完整，请先读取完当前字节的所有位')
        return self.data[self._offset_byte:]

    def position(self):
        return self._offset_byte, self._offset_bit

    def mark(self):
        self._marked_offset_byte = self._offset_byte
        self._marked_offset_bit = self._offset_bit
        return self

    def reset(self):
        self._offset_byte = self._marked_offset_byte
        self._offset_bit = self._marked_offset_bit

    def _check_bits(self, n):
        if n > (len(self.data) - self._offset_byte) * 8 - self._offset_bit:
            raise RuntimeError('剩余数据不足{}位'.format(n))
        if n > 8 - self._offset_bit:
            raise RuntimeError('不能跨字节读取读取位')

    def _move_bits(self, n):
        self._offset_bit += n
        if self._offset_bit == 8:
            self._offset_bit = 0
            self._offset_byte += 1

    def _check_bytes(self, n):
        if not self._offset_bit == 0:
            raise RuntimeError('当前字节不完整，请先读取完当前字节的所有位')
        if n > len(self.data) - self._offset_byte:
            raise RuntimeError('剩余数据不足{}个字节'.format(n))

    def _move_bytes(self, n):
        self._offset_byte += n
