import subprocess
import paho.mqtt.client as mqtt
import time
import json
from logger.logger import setup_applevel_logger
from dotenv import load_dotenv
from player import Player
from media_handlers.url_handler import URLHandler
from media_handlers.video_handler import VideoHandler
from media_handlers.playlist_handler import PlaylistHandler
import os
from pathlib import Path
from utils import publish_message

load_dotenv()

logger = setup_applevel_logger(__name__)

BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0])
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

SERIAL_NO = os.getenv('SERIAL_NO')

MQTT_HOST = "test.mosquitto.org"

if not SERIAL_NO:
    logger.error('Serial no not found')
    exit()

def format_topic_name(x): return f'{SERIAL_NO}-{x}'

class APP:
    def __init__(self):
        self.client = None 
        self.player = Player()
    
    def on_mqtt_connect(self,client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to broker")
            publish_message(self.client,"NODE_STATE",{"serialNo":SERIAL_NO,"status":"Idle"},qos=1)
            client.subscribe(format_topic_name("DISPLAY_URL"))
            client.subscribe(format_topic_name("STOP_MEDIA"))
            client.subscribe(format_topic_name("PLAY_VIDEO"))
            client.subscribe(format_topic_name("PLAY_PLAYLIST"))
        else:
            logger.error("Connection failed")
    
    def on_mqtt_disconnect(self,client, userdata, message):
        logger.info('Disconnected from the broker')

    def on_mqtt_message(self,client, userdata, message):
        logger.info("Message received : "  + str(message.payload) + " on " + message.topic)

        if message.topic == format_topic_name("DISPLAY_URL"):
            self.terminate_all_active_media()
            url_handler = URLHandler(client=client,message=message,serialNo=SERIAL_NO)
            url_handler.play()
        
        if message.topic == format_topic_name("STOP_MEDIA"):
            self.terminate_all_active_media()

        if message.topic == format_topic_name("PLAY_VIDEO"):
            # self.terminate_all_active_media()
            video_handler = VideoHandler(client=client,message=message,player=self.player,serialNo=SERIAL_NO,dir=VIDEOS_DIR)
            video_handler.play()

        if message.topic == format_topic_name("PLAY_PLAYLIST"):
            self.terminate_all_active_media()
            playlist_handler = PlaylistHandler(client=client,message=message,player=self.player,serialNo=SERIAL_NO,dir=VIDEOS_DIR)
            playlist_handler.play()

    def terminate_all_active_media(self):
        publish_message(self.client,"NODE_STATE",{"serialNo":SERIAL_NO,"status":"Idle"})
        logger.info('Terminating all active media')
        subprocess.call(["pkill", "firefox"])
        self.player.terminate()
        
    def start(self):
        try:
            self.client = mqtt.Client(SERIAL_NO)
            self.client.will_set('NODE_STATE',payload=str(json.dumps({"serialNo":SERIAL_NO,"status":'Offline'})),qos=2,retain=True)
            self.client.connect(host=MQTT_HOST)
            self.client.on_connect= self.on_mqtt_connect   
            self.client.on_disconnect = self.on_mqtt_disconnect
            self.client.on_message= self.on_mqtt_message
            self.client.loop_forever()
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            self.start() 

app = APP()

app.start()

