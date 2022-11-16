import subprocess
import requests
import paho.mqtt.client as mqtt
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

def publish_message(topic,message):
    try:
        host = "test.mosquitto.org"
        client = mqtt.Client(SERIAL_NO)
        client.connect(host=host)
        client.publish(topic,str(json.dumps(message)))
        logger.info(f"Published: {message}")
        client.disconnect()
    except Exception as e:
        logger.error(e)


def start_app():
    try:
        host = "test.mosquitto.org"
        client = mqtt.Client(SERIAL_NO)
        client.will_set('NODE_STATE',payload=str(json.dumps({"serialNo":SERIAL_NO,"status":'Offline'})),qos=1,retain=True)
        client.connect(host=host)
        client.publish('NODE_STATE',str(json.dumps({"serialNo":SERIAL_NO,"status":'Idle'})),qos=1)
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

def play_video(filepath,loop,id):
    publish_message("NODE_STATE",{"serialNo":SERIAL_NO,"status":"Playing","playingData":{"type":"Video","mediaId":id}})
    PLAYER.play([filepath],loop)



def play_playlist(videos,loop,id):
    playlist = []

    for video in videos:
        filepath = file_path(video['name'])
        playlist.append(filepath)

    publish_message("NODE_STATE",{"serialNo":SERIAL_NO,"status":"Playing","playingData":{"type":"VideoList","mediaId":id}})
    PLAYER.play(playlist,loop)





def play_video_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = json.loads(data)

    id = newData['id']
    name = newData['name']
    url = newData['path']
    loop = newData['loop']

    # print(loop)

    # TODO: validate the dict 

    filepath = file_path(name)

    if os.path.exists(filepath):
        logger.info('video already exists skipping download')
        play_video(filepath,loop,id)
    else:
        logger.info('downloading video')
        download_video_from_url(url,filepath)
        play_video(filepath,loop,id)

def play_playlist_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = json.loads(data)

    id = newData['id']
    videos  = newData['playlist']
    loop = newData['loop']

    # TODO: validate the dict 

    for video in videos:
        filepath = file_path(video['name'])
        if not os.path.exists(filepath):
            download_video_from_url(video['path'],filepath)
    
    play_playlist(videos,loop,id)


def display_url(url,id):
    publish_message("NODE_STATE",{"serialNo":SERIAL_NO,"status":"Playing","playingData":{"type":"Url","mediaId":id}})
 
    logger.info(f'URL received: {url}')
    subprocess.call(["firefox", f"--kiosk={url}"])


def close_browser(secs):
    time.sleep(secs)
    subprocess.call(["pkill", "firefox"])
    publish_message("NODE_STATE",{"serialNo":SERIAL_NO,"status":"Idle"})





def display_url_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = json.loads(data)

    logger.info("Message received: {newData}")
    id = newData['id']

    url = newData["url"]
    seconds = newData["seconds"]

    if not url:
        logger.error('URL not found')
        return
    t1 = Thread(target=display_url, args=(url,id,))
    t2 = Thread(target=close_browser, args=(seconds,))

    t1.start()
    t2.start()

def stop_media_handler():
    publish_message("NODE_STATE",{"serialNo":SERIAL_NO,"status":"Idle"})
    logger.info('Terminating all active media')
    subprocess.call(["pkill", "firefox"])
    PLAYER.teminate()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to broker")
        client.subscribe(format_topic_name("DISPLAY_URL"))
        client.subscribe(format_topic_name("STOP_MEDIA"))
        client.subscribe(format_topic_name("PLAY_VIDEO"))
        client.subscribe(format_topic_name("PLAY_PLAYLIST"))
    else:
        logger.error("Connection failed")

def on_message(client, userdata, message):
    logger.info("Message received : "  + str(message.payload) + " on " + message.topic)

    if message.topic == format_topic_name("DISPLAY_URL"):
        stop_media_handler()
        display_url_handler(message)
    
    if message.topic == format_topic_name("STOP_MEDIA"):
        stop_media_handler()

    if message.topic == format_topic_name("PLAY_VIDEO"):
        stop_media_handler()
        play_video_handler(message)

    if message.topic == format_topic_name("PLAY_PLAYLIST"):
        stop_media_handler()
        play_playlist_handler(message)


start_app()
           
      




