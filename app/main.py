import subprocess
import requests
import paho.mqtt.client as mqtt
import ast 
import os
import time
import json
from pathlib import Path
from threading import Thread
from logger.logger import setup_applevel_logger
from dotenv import load_dotenv
from player import Player


load_dotenv()

logger = setup_applevel_logger(__name__)

BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0])
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

def file_path(x): return os.path.join(VIDEOS_DIR, x)


if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

SERIAL_NO = os.getenv('SERIAL_NO')

if not SERIAL_NO:
    logger.error('Serial no not found')
    exit()

def format_topic_name(x): return f'{SERIAL_NO}-{x}'

PLAYER = Player()

def start_app():
    try:
        host = "test.mosquitto.org"
        client = mqtt.Client(SERIAL_NO)
        client.connect(host=host)
        client.on_connect= on_connect    
        client.on_message= on_message
        client.loop_forever()
    except Exception as e:
        logger.error(e)
        time.sleep(1)
        start_app() 

def download_video_from_url(url,path):
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)

def play_video(filepath,loop):
    stop_media_handler()
    PLAYER.teminate()
    time.sleep(1)
    PLAYER.play([filepath],loop)


def play_video_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = json.loads(data)

    name = newData['name']
    url = newData['path']
    loop = newData['loop']

    # print(loop)

    # TODO: validate the dict 

    filepath = file_path(name)

    if os.path.exists(filepath):
        logger.info('video already exists skipping download')
        play_video(filepath,loop)
    else:
        logger.info('downloading video')
        download_video_from_url(url,filepath)
        play_video(filepath,loop)

 

def display_url(url):
    stop_media_handler()
    logger.info(f'URL received: {url}')
    subprocess.call(["firefox", f"--kiosk={url}"])


def close_browser(secs):
    time.sleep(secs)
    subprocess.call(["pkill", "firefox"])



def display_url_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = json.loads(data)

    logger.info("Message received: {newData}")

    url = newData["url"]
    seconds = newData["seconds"]

    if not url:
        logger.error('URL not found')
        return
    t1 = Thread(target=display_url, args=(url,))
    t2 = Thread(target=close_browser, args=(seconds,))

    t1.start()
    t2.start()

def stop_media_handler():
    logger.info('Terminating all active media')
    subprocess.call(["pkill", "firefox"])
    PLAYER.teminate()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to broker")
        client.subscribe(format_topic_name("DISPLAY_URL"))
        client.subscribe(format_topic_name("STOP_MEDIA"))
        client.subscribe(format_topic_name("PLAY_VIDEO"))
    else:
        logger.error("Connection failed")

def on_message(client, userdata, message):
    logger.info("Message received : "  + str(message.payload) + " on " + message.topic)

    if message.topic == format_topic_name("DISPLAY_URL"):
        display_url_handler(message)
    
    if message.topic == format_topic_name("STOP_MEDIA"):
        stop_media_handler()

    if message.topic == format_topic_name("PLAY_VIDEO"):
        play_video_handler(message)


start_app()
           
      




