from logger.logger import setup_applevel_logger
import json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import os
from pathlib import Path

load_dotenv()

logger = setup_applevel_logger(__name__)

MAX_VIDEO_STORAGE_SIZE = int(os.getenv(
    'MAX_VIDEO_STORAGE_SIZE', 20000000000))

BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0])

VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

VIDEOS_PLAYBACK_HISTORY_PATH = os.path.join(
    BASE_DIR, "videos/playback_history.json")


def publish_message(client: mqtt.Client | None, topic: str, message, qos=0):
    if not client:
        logger.error('Mqtt client is None')
        return
    try:
        client.publish(topic, str(json.dumps(message)), qos=qos)
        logger.info(f"Published: {message}")
    except Exception as e:
        logger.error(e)


def get_data_from_message(message):
    try:
        data_str = str(message.payload.decode("utf-8"))
        return json.loads(data_str)
    except Exception as e:
        logger.error(e)


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    return json_data


def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def check_and_create_file(file_path, initial_content=None):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            if initial_content:
                logger.info(f"Initial content: '{initial_content}'")
                file.write(initial_content)
        logger.info(f"File '{file_path}' created.")
    else:
        logger.info(f"File '{file_path}' already exists.")
