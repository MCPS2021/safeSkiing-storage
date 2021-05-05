import logging
from paho.mqtt.client import Client
from config import cfg
import re
from db import Stations, Skiipass, StationsHistory, LastUpdate

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


def parse_topic(message_topic):
    if message_topic.find("UUIDs") != -1:
        return "station-topic"
    elif message_topic.find("NFC") != -1:
        return "nfc-topic"
    elif message_topic.find("totalPeople") != -1:
        return "totalpeople-topic"
    else:
        return None


def handle_station_topic(topic, message_payload):
    logging.info("TODO: handle_station_topic")
    logging.info(message_payload)


def handle_nfc_topic(topic, message_payload):
    logging.info("TODO: handle_nfc_topic")
    logging.info(message_payload)


def handle_totalpeople_topic(topic, message_payload):
    pattern = "/station(.*?)/totalPeople"
    station_id = re.search(pattern, topic).group(1)
    logging.info(message_payload + " people on station " + station_id)
    logging.info("TODO: handle_totalpeople_topic")


if __name__ == "__main__":

    logging.info("Start mqqt subscribe")

    client = Client(client_id=cfg["mqtt"]["client_id"])


    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.connected_flag = True  # set flag
            logging.info("connected OK Returned code=%s", rc)
        else:
            logging.info("Bad connection Returned code=%s", rc)


    def on_message(client, userdata, message):
        topic = parse_topic(message.topic)
        message_payload = message.payload.decode()
        if topic == 'station-topic':
            handle_station_topic(message.topic, message_payload)
        elif topic == 'nfc-topic':
            handle_nfc_topic(message.topic, message_payload)
        elif topic == 'totalpeople-topic':
            handle_totalpeople_topic(message.topic, message_payload)


    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost")
    qos = cfg["mqtt"]["qos"]
    client.subscribe([
        (cfg["mqtt"]["station-topic"], qos),
        (cfg["mqtt"]["nfc-topic"], qos),
        (cfg["mqtt"]["totalpeople-topic"], qos)
    ])

    client.loop_forever()

    logging.info("Finish...")
