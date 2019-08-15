import logging

from client import Client

mqtt_client = Client('127.0.0.1', username='derker', password='123456')


@mqtt_client.on_connect
def on_connect(connack_packet):
    logging.info('[on_connect]: sp = {}, return_code = {}'.format(connack_packet.sp, connack_packet.return_code))
    # mqtt_client.subscribe('$SYS/broker/version', 2)
    mqtt_client.publish('hello', bytes('I\'m derker', 'utf8'), 2)


@mqtt_client.on_message
def on_message(message):
    logging.info('[on_message]: {}'.format(message))


if __name__ == '__main__':
    mqtt_client.connect()
    mqtt_client.loop_forever()
