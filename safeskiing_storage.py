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
    '''
    mosquitto_pub -t /station1/UUIDs -m "<uuid>,battery;<uuid>,battery;<uuid>,battery;<uuid>,battery"
    '''
    logging.info("handle_station_topic topic=[%s], message_payload=[%s]", topic, message_payload)
    pattern = "/station(.*?)/UUIDs"
    station_id = re.search(pattern, topic).group(1)
    logging.info("station_id=[%s]", station_id)
    logging.info(message_payload)
    skiers = message_payload.split(";")
    for skier in skiers:
        uuid_battery = skier.split(",")
        uuid = uuid_battery[0]
        battery = uuid_battery[1]
        logging.info("UUID=[%s], battery=[%s]", uuid, battery)



def handle_nfc_topic(topic, message_payload):
    '''
    mosquitto_pub -t /NFC/uuid-aaa-bbb-ccc -m ff
    '''
    logging.info("handle_nfc_topic topic=[%s], message_payload=[%s]", topic, message_payload)
    logging.info(message_payload)
    uuid = topic.split("/NFC/", 1)[1]
    battery = int(message_payload, 16)
    logging.info("UUID=[%s], battery=[%s]", uuid, battery)


def handle_totalpeople_topic(topic, message_payload):
    '''
    mosquitto_pub -t /station1/totalPeople -m 34
    '''
    logging.info("handle_totalpeople_topic topic=[%s], message_payload=[%s]", topic, message_payload)
    pattern = "/station(.*?)/totalPeople"
    station_id = re.search(pattern, topic).group(1)
    logging.info(message_payload + " people on station " + station_id)



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
