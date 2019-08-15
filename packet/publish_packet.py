from util.decode import skip_remaining_length_byte
from util.encode import encode_remaining_length, encode_string, encode_int16
from util.scanner import Scanner


class PublishPacket:

    def __init__(self, dup: bool, qos: int, retain: bool, topic: str, packet_id: int, payload: bytes):
        self._dup = dup
        self._qos = qos
        self._retain = retain
        self._topic = topic
        self._packet_id = packet_id
        self._payload = payload

    @property
    def dup(self):
        return self._dup

    @property
    def qos(self):
        return self._qos

    @property
    def retain(self):
        return self._retain

    @property
    def topic(self):
        return self._topic

    @property
    def packet_id(self):
        return self._packet_id

    @property
    def payload(self):
        return self._payload

    def to_bytes(self):
        byte_array = bytearray()
        # packet type
        first_byte = 0b00110000
        # dup
        if self._dup:
            first_byte = first_byte | 0b00111000
        # qos
        first_byte = first_byte | (self._qos << 1)
        # retain
        if self._retain:
            first_byte = first_byte | 1
        byte_array.append(first_byte)
        # remaining length
        remaining_length_bytes = self._cal_remaining_length_bytes()
        byte_array.extend(remaining_length_bytes)
        # topic
        topic_bytes = encode_string(self._topic)
        byte_array.extend(topic_bytes)
        # packet id (when QoS = 1 or 2)
        if not self._qos == 0:
            packet_id_bytes = encode_int16(self._packet_id)
            byte_array.extend(packet_id_bytes)
        # payload
        if self._payload:
            byte_array.extend(self._payload)

        return bytes(byte_array)

    @staticmethod
    def from_bytes(packet_bytes):
        scanner = Scanner(packet_bytes)
        # skip packet type
        scanner.skip_bits(4)
        # dup
        dup = scanner.next_bits()
        # qos
        qos = scanner.next_bits(2)
        # retain
        retain = bool(scanner.next_bits())
        # skip Remaining Length
        skip_remaining_length_byte(scanner)
        # topic name length
        topic_length = scanner.next_bytes(2)
        # topic name
        topic_bytes = bytearray()
        for i in range(topic_length):
            topic_bytes.append(scanner.next_bytes())
        topic = bytes(topic_bytes).decode('utf-8')
        # packet id
        packet_id = None
        if not qos == 0:
            packet_id = scanner.next_bytes(2)
        payload = scanner.remains_bytes()
        return PublishPacket(dup, qos, retain, topic, packet_id, payload)

    def __str__(self):
        return 'PublishPacket(dup = {}, qos = {}, retain = {}, topic= {}, packet_id = {}, payload = {})' \
            .format(self._dup, self._qos, self._retain, self._topic, self._packet_id, self._payload)

    def _cal_remaining_length_bytes(self):
        # topic length
        length = 2
        # topic
        length += len(bytes(self._topic, 'utf8'))
        # packet id (when QoS = 1 or 2)
        if not self._qos == 0:
            length = length + 2
        # payload
        if self._payload:
            length = length + len(self._payload)
        return encode_remaining_length(length)
