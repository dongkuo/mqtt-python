from util.encode import encode_remaining_length, encode_string


class ConnectPacket:
    """A connect packet"""

    def __init__(self, client_id, username=None, password=None, keep_alive=300,
                 will_topic=None, will_message=None, will_retain=False, will_qos=0, clean_session_flag=True):
        self._client_id = client_id
        self._username = username
        self._password = password
        self._keep_alive = keep_alive
        self._will_topic = will_topic
        self._will_message = will_message
        self._will_retain = will_retain
        self._will_qos = will_qos
        self._clean_session_flag = clean_session_flag

    def to_bytes(self):
        """convert connect packet to bytes"""
        byte_array = bytearray()
        # Packet type and Reserved
        byte_array.append(0x10)
        # Remaining Length
        remaining_length_bytes = self._cal_remaining_length_bytes()
        byte_array.extend(remaining_length_bytes)
        # Protocol Name
        byte_array.extend([0, 4, 77, 81, 84, 84])
        # Protocol Level
        byte_array.append(4)
        #  Connect Flags
        flags_byte = self._cal_flags_byte()
        byte_array.append(flags_byte)
        # KeepAlive
        byte_array.extend(self._cal_keep_alive_bytes())
        # Payload
        byte_array.extend(self._cal_payload_bytes())

        return bytes(byte_array)

    def _cal_remaining_length_bytes(self):
        """计算 Remaining Length 字节
        Remaining Length  = ProtocolName(6) + ProtocolLevel(1) + ConnectFlags(1) + KeepAlive(2) + Payload(ClientId
                            + WillTopic + WillMessage + UserName + Password)
        """
        remaining_length = 10
        if self._client_id:
            remaining_length += 2 + len(bytes(self._client_id, 'utf-8'))
        if self._will_topic:
            remaining_length += 2 + len(bytes(self._will_topic, 'utf-8'))
        if self._will_message:
            remaining_length += 2 + len(bytes(self._will_message, 'utf-8'))
        if self._username:
            remaining_length += 2 + len(bytes(self._username, 'utf-8'))
        if self._password:
            remaining_length += 2 + len(bytes(self._password, 'utf-8'))
        return encode_remaining_length(remaining_length)

    def _cal_flags_byte(self):
        """计算 Connect Flags 字节"""
        username_flag = 0
        if self._username:
            username_flag = 0b1000_0000

        password_flag = 0
        if self._password:
            password_flag = 0b0100_0000

        will_retain_flag = 0
        if self._will_retain:
            password_flag = 0b0010_0000

        will_qos = self._will_qos << 3 if self._will_topic and self._will_message else 0

        will_flag = 0
        if self._will_topic and self._will_message:
            will_flag = 0b0000_0100

        clean_session_flag = 0
        if self._clean_session_flag:
            clean_session_flag = 0b0000_0010

        return username_flag | password_flag | will_retain_flag | will_qos | will_flag | clean_session_flag

    def _cal_keep_alive_bytes(self):
        return self._keep_alive.to_bytes(length=2, byteorder='big', signed=False)

    def _cal_payload_bytes(self):
        """ Payload = ClientId + WillTopic + WillMessage + UserName + Password
        """
        bs = bytearray()
        bs.extend(encode_string(self._client_id))
        bs.extend(encode_string(self._will_topic))
        bs.extend(encode_string(self._will_message))
        bs.extend(encode_string(self._username))
        bs.extend(encode_string(self._password))
        return bytes(bs)


if __name__ == '__main__':
    packet = ConnectPacket('1', 'derker', '123456', keep_alive=60)
    print(packet.to_bytes())
