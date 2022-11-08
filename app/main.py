import subprocess
import requests
import paho.mqtt.client as mqtt
import ast 
import os
import time
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

NEW_PLAYER = None

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

def play_video(filepath):
    # TODO: find a way to terminate the player
    player = Player()
    player.play([filepath])


def play_video_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = ast.literal_eval(data)

    name = newData['name']
    url = newData['path']

    # TODO: validate the dict 

    filepath = file_path(name)

    if os.path.exists(filepath):
        logger.info('video already exists skipping download')
        play_video(filepath)
    else:
        logger.info('downloading video')
        download_video_from_url(url,filepath)
        play_video(filepath)

 

def display_url(url):
    logger.info(f'URL received: {url}')
    subprocess.call(["pkill", "firefox"])
    subprocess.call(["firefox", f"--kiosk={url}"])

def display_url_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = ast.literal_eval(data)

    logger.info("Message received: {newData}")

    url = newData["url"]
    if not url:
        logger.error('URL not found')
        return
    t = Thread(target=display_url, args=(url,))
    t.start()

def stop_media_handler():
    logger.info('Terminating all active media')
    subprocess.call(["pkill", "firefox"])
    subprocess.call(["pkill", "mpv"])

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to broker")
        client.subscribe("DISPLAY_URL")
        client.subscribe("STOP_MEDIA")
        client.subscribe("PLAY_VIDEO")
    else:
        logger.error("Connection failed")

def on_message(client, userdata, message):
    logger.info("Message received : "  + str(message.payload) + " on " + message.topic)

    if message.topic == "DISPLAY_URL":
        display_url_handler(message)
    
    if message.topic == "STOP_MEDIA":
        stop_media_handler()

    if message.topic == "PLAY_VIDEO":
        play_video_handler(message)


start_app()
           
      




