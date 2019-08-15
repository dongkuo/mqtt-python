import logging
import socket
import sys
import traceback

from packet.connack_packet import ConnackPacket
from packet.connect_packet import ConnectPacket
from packet.puback_packet import PubackPacket
from packet.pubcomp_packet import PubcompPacket
from packet.publish_packet import PublishPacket
from packet.pubrec_packet import PubrecPacket
from packet.pubrel_packet import PubrelPacket
from packet.suback_packet import SubackPacket
from packet.subscribe_packet import SubscribePacket
from util.common import random_str, merge_dict

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', stream=sys.stdout, level=logging.DEBUG)

_default_options = {
    "keepalive": 60,
    "will_topic": None,
    "will_message": None,
    "will_retain": None,
    "will_qos": None,
    "clean_session": True,
    "ping_interval": 300,
}

_receive_packet_types = {
    2: ConnackPacket,
    3: PublishPacket,
    4: PubackPacket,
    5: PubrecPacket,
    6: PubrelPacket,
    7: PubcompPacket,
    9: SubackPacket,
}


class Client:

    def __init__(self, host, port=1883, client_id=random_str(6), username=None, password=None, **options):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._client_id = client_id
        self._options = merge_dict(_default_options, options)
        # No default callbacks
        self._on_connect = None
        self._on_message = None
        self._socket = None
        self._packet_id = 0
        self._unack_package_ids = set()
        self._unack_packet = {}

    @classmethod
    def define_packet_type(cls, packet_type):

        def inner(func):
            _receive_packet_types[packet_type] = func
            return func

        return inner

    def connect(self):
        """connect MQTT broker
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(True)
        self._socket.connect((self._host, self._port))
        # Send connect packet
        packet = ConnectPacket(self._client_id, self._username, self._password, self._options['keepalive'],
                               self._options['will_topic'], self._options['will_message'], self._options['will_retain'],
                               self._options['will_qos'], self._options['clean_session'])
        self._send_packet(packet)

    def reconnect(self):
        """reconnect MQTT broker"""
        pass

    def close(self):
        """close connection and clear the resource
        """
        pass

    def loop_forever(self):
        """Receive data from broker in an loop"""
        while True:
            try:
                packet_type, flags, packet_bytes, remaining_length = self._recv_packet()
                if packet_type not in _receive_packet_types:
                    logging.warning("unknown packet type: %s", packet_type)
                    continue
                packet = _receive_packet_types[packet_type].from_bytes(packet_bytes)
                logging.debug('receive a packet: %s', packet)

                # CONNACK Packet
                if isinstance(packet, ConnackPacket) and self._on_connect:
                    self._on_connect(packet)
                # Publish Packet
                elif isinstance(packet, PublishPacket):
                    if packet.qos == 0:
                        # callback on_message
                        self._on_message(packet)
                    elif packet.qos == 1:
                        # callback on_message
                        self._on_message(packet)
                        # publish ack for publish packet(qos = 1)
                        self._send_packet(PubackPacket(packet.packet_id))
                    elif packet.qos == 2:
                        # Store packet id
                        self._unack_package_ids.add(packet.packet_id)
                        # callback on_message
                        self._on_message(packet)
                        # send PUBREC packet
                        self._send_packet(PubrecPacket(packet.packet_id))
                # PUBACK Packet
                elif isinstance(packet, PubackPacket) and packet.packet_id in self._unack_packet:
                    self._unack_packet.pop(packet.packet_id)
                # PUBREC Packet
                elif isinstance(packet, PubrecPacket) and packet.packet_id in self._unack_packet:
                    # discard message
                    self._unack_packet.pop(packet.packet_id)
                    # store packet id
                    self._unack_package_ids.add(packet.packet_id)
                    # send PUBREL message
                    self._send_packet(PubrelPacket(packet.packet_id))
                # PUBCOMP Packet
                elif isinstance(packet, PubcompPacket) and packet.packet_id in self._unack_package_ids:
                    self._unack_package_ids.remove(packet.packet_id)
                # PUBREL Packet
                elif isinstance(packet, PubrelPacket) and packet.packet_id in self._unack_package_ids:
                    # discard packet id
                    self._unack_package_ids.remove(packet.packet_id)
                    # send PUBCOMP packet
                    self._send_packet(PubcompPacket(packet.packet_id))

            except KeyboardInterrupt:
                self.close()
            except ConnectionError as e:
                logging.warning("%s", e)
                return
            except Exception as e:
                logging.error("mqtt client occur error: %s", e)
                traceback.print_exc()
                continue

    def on_connect(self, func):
        """
        """
        self._on_connect = func
        return func

    def on_message(self, func):
        """
        """
        self._on_message = func
        return func

    def subscribe(self, topic: str, qos=0, *others_topic_qos):
        """订阅消息
        """
        packet = SubscribePacket(self._next_packet_id(), topic, qos, *others_topic_qos)
        self._send_packet(packet)

    def unsubscribe(self, topics):
        """取消订阅
        """
        pass

    def publish(self, topic: str, message: bytes, qos: int = 0, retain: bool = False, dup: bool = False):
        """发布消息
        """
        if qos != 2:
            dup = False
        publish_packet = PublishPacket(dup, qos, retain, topic, self._next_packet_id(), message)
        self._send_packet(publish_packet)

        if qos != 0:
            # Store message
            self._unack_packet[publish_packet.packet_id] = publish_packet

    def _send_packet(self, packet):
        """发送数据包"""
        logging.debug('send a packet: {}'.format(packet))
        packet_bytes = packet.to_bytes()
        self._socket.sendall(packet_bytes)

    def _recv_packet(self):
        packet_bytes = bytearray()
        # Read first byte
        read_bytes = self._socket.recv(1)
        self._check_recv_data(read_bytes)
        first_byte = read_bytes[0]
        packet_bytes.append(first_byte)
        packet_type = first_byte >> 4
        flags = first_byte & 0x0F

        # Read second byte
        read_bytes = self._socket.recv(1)
        self._check_recv_data(read_bytes)
        second_byte = read_bytes[0]
        packet_bytes.append(second_byte)

        remaining_length = second_byte & 0x7F
        flag_bit = second_byte & 0x80
        multiplier = 1
        while True:
            if flag_bit == 0:
                break
            read_bytes = self._socket.recv(1)
            self._check_recv_data(read_bytes)
            next_byte = read_bytes[0]
            flag_bit = next_byte & 0x80
            remaining_length += (next_byte & 0x7F) * multiplier

        # Read remaining bytes
        while remaining_length > 0:
            read_bytes = self._socket.recv(min(4096, remaining_length))
            remaining_length -= len(read_bytes)
            packet_bytes.extend(read_bytes)
        return packet_type, flags, packet_bytes, remaining_length

    @staticmethod
    def _check_recv_data(data):
        if not data:
            raise ConnectionError('connection is closed')

    def _next_packet_id(self):
        self._packet_id += 1
        return self._packet_id
