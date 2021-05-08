import logging
from paho.mqtt.client import Client
from config import cfg
import re
from db import Stations, Skiipass, StationsHistory, LastUpdate, session
from datetime import datetime

# define logger
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


def handle_station_topic(topic, message_payload):
    """
    On this topic all the UUID, detected by lift facility station_id, are published
    Publisher example:
        mosquitto_pub -t /station1/UUIDs -m "<uuid>,battery;<uuid>,battery;<uuid>,battery;<uuid>,battery"
    """
    logging.info("handle_station_topic")
    pattern = "/station(.*?)/UUIDs"
    station_id = re.search(pattern, topic).group(1)
    logging.info("station_id=[%s]", station_id)

    station = session.query(Stations).get(station_id)
    logging.info("station found=[%s]", station)
    skiers = message_payload.split(";")
    total_people_now = len(skiers)
    logging.info("total_people_now found=[%s]", total_people_now)
    for skier in skiers:
        uuid_battery = skier.split(",")
        uuid = uuid_battery[0]
        battery = int(uuid_battery[1], 16)
        logging.info("UUID=[%s], battery=[%s]", uuid, battery)

        last_update_check = session.query(LastUpdate).get(uuid)
        logging.info("last_update_check [%s]", last_update_check)
        if last_update_check is None:
            logging.info("last_update not found, create and insert a new one")
            last_update = LastUpdate(uuid=uuid,
                                     last_battery=battery,
                                     last_update=datetime.now(),
                                     station=station,
                                     last_position_change=datetime.now(),
                                     total_people=total_people_now)
            session.add(last_update)
            logging.info("inserted last_update [%s]", last_update)
        else:
            logging.info("last_update found, try to update")
            if last_update_check.station.id != station_id:
                logging.info("last station is different, update last position change and total people")
                last_update_check.last_position_change = datetime.now()
                last_update_check.total_people = total_people_now

            if last_update_check.total_people < total_people_now:
                logging.info("total people is greater then last check, update it")
                last_update_check.total_people = total_people_now

            last_update_check.station = station
            last_update_check.last_battery = battery
            last_update_check.last_update = datetime.now()
            last_update_check.total_people = total_people_now
            logging.info("prepared for last_update done [%s]", last_update_check)

        logging.info("try to commit...")
        session.commit()
        logging.info("committed")


def handle_nfc_topic(topic, message_payload):
    """
    On this topic a device publish the station id
    Publisher example:
        mosquitto_pub -t /NFC/uuid-aaa-bbb-ccc -m 1
    """
    logging.info("handle_nfc_topic")
    uuid = topic.split("/NFC/", 1)[1]
    station_id = message_payload
    logging.info("UUID=[%s], station_id=[%s]", uuid, station_id)
    station = session.query(Stations).get(station_id)
    logging.info("station found=[%s]", station)
    last_update = session.query(LastUpdate).get(uuid)
    logging.info("last_update [%s]", last_update)
    if last_update is not None:
        logging.info("last_update found, create new skiipass")
        skiipass = Skiipass(uuid=uuid,
                            departure_time=datetime.now(),
                            arrival_time=last_update.last_position_change,
                            station=station,
                            total_people=last_update.total_people)
        logging.info("add skiipass %s", skiipass)
        session.add(skiipass)
        logging.info("try to commit...")
        session.commit()
        logging.info("committed")
    else:
        logging.warning("last_update not found!")


def handle_totalpeople_topic(topic, message_payload):
    """
    On this topic the number of beacons detected by lift facility station_id is published
    Publisher example:
        mosquitto_pub -t /station1/totalPeople -m 34
    """
    logging.info("handle_totalpeople_topic")
    pattern = "/station(.*?)/totalPeople"
    station_id = re.search(pattern, topic).group(1)
    total_people_now = message_payload
    logging.info("station_id=[%s], people=[%s]", station_id, total_people_now)

    station = session.query(Stations).get(station_id)
    logging.info("station found=[%s]", station)

    stations_history = StationsHistory(station=station,
                                       instant=datetime.now(),
                                       total_people=total_people_now)
    logging.info("add stations_history %s", stations_history)
    session.add(stations_history)
    logging.info("try to commit...")
    session.commit()
    logging.info("committed")


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

        message_topic = message.topic
        message_payload = message.payload.decode()
        logging.info("Handle new message topic=[%s], message_payload=[%s]", message_topic, message_payload)

        if message_topic.find("UUIDs") != -1:
            handle_station_topic(message.topic, message_payload)
        elif message_topic.find("NFC") != -1:
            handle_nfc_topic(message.topic, message_payload)
        elif message_topic.find("totalPeople") != -1:
            handle_totalpeople_topic(message.topic, message_payload)
        else:
            logging.warning("Handler for this topic not found!!!")
            return None


    client.on_connect = on_connect
    client.on_message = on_message

    logging.info("Try connect...")
    client.connect(cfg['mqtt']['host'])
    logging.info("...connected")

    logging.info("Try to subscribe...")
    qos = cfg["mqtt"]["qos"]
    client.subscribe([
        (cfg["mqtt"]["station-topic"], qos),
        (cfg["mqtt"]["nfc-topic"], qos),
        (cfg["mqtt"]["totalpeople-topic"], qos)
    ])
    logging.info("...subscribed")

    logging.info("Go to loop forever...")
    client.loop_forever()

    logging.info("Finish...")
