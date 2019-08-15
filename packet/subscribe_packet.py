from util.encode import encode_remaining_length, encode_int16


class SubscribePacket:

    def __init__(self, packet_id: int, topic: str, qos: int, *others_topic_qos):
        if packet_id > 0xFFFF:
            packet_id = packet_id % 0xFFFF
        self._packet_id = packet_id
        self._items = [(topic, qos)]
        if len(others_topic_qos) % 2 != 0:
            raise ValueError('the number of topic must match the number of qos')
        for i in range(0, len(others_topic_qos) // 2):
            self._items.append((others_topic_qos[i * 2], others_topic_qos[i * 2 + 1]))

    def to_bytes(self):
        byte_array = bytearray()
        # Packet type and Reserved
        byte_array.append(0b10000010)
        # Remaining Length
        byte_array.extend(self._cal_remaining_length_bytes())
        # Packet Identifier MSB, LSB
        byte_array.extend(encode_int16(self._packet_id))
        # payload
        byte_array.extend(self._cal_payload_bytes())
        return bytes(byte_array)

    def _cal_remaining_length_bytes(self):
        """
        Remaining Length = 2 + ∑(2 + Topic length + 1)
        """
        remaining_length = 2
        for topic_qos in self._items:
            remaining_length += 3 + len(bytes(topic_qos[0], 'utf-8'))
        return encode_remaining_length(remaining_length)

    def _cal_payload_bytes(self):
        byte_array = bytearray()
        for topic_qos in self._items:
            topic_length = len(bytes(topic_qos[0], 'utf-8'))
            topic_length_bytes = encode_int16(topic_length)
            # Length MSB, LSB
            byte_array.extend(topic_length_bytes)
            # Topic
            byte_array.extend(bytes(topic_qos[0], 'utf-8'))
            # QoS
            byte_array.append(topic_qos[1])
        return bytes(byte_array)
