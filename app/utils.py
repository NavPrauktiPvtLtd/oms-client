from logger.logger import setup_applevel_logger 
import json
import paho.mqtt.client as mqtt
import os
from pathlib import Path

logger = setup_applevel_logger(__name__)

BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0])
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

def publish_message(client:mqtt.Client|None,topic:str,message,qos=0):
    if not client:
        logger.error('Mqtt client is None')
        return
    try:
        client.publish(topic,str(json.dumps(message)),qos=qos)
        logger.info(f"Published: {message}")
    except Exception as e:
        logger.error(e)

def get_data_from_message(message):
    try:
        dataStr = str(message.payload.decode("utf-8"))
        return json.loads(dataStr)
    except Exception as e:
        logger.error(e)