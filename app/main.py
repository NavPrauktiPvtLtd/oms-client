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
        self.player = None
    
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


    def on_media_video(self, client, userdata, message):
        self.terminate_all_active_media()
        video_handler = VideoHandler(client=client,message=message,player=self.player,serialNo=SERIAL_NO,dir=VIDEOS_DIR)
        video_handler.play()
    
    def on_media_playlist(self, client, userdata, message):
        self.terminate_all_active_media()
        playlist_handler = PlaylistHandler(client=client,message=message,player=self.player,serialNo=SERIAL_NO,dir=VIDEOS_DIR)
        playlist_handler.play()

    def on_media_url(self, client, userdata, message):
        self.terminate_all_active_media()
        url_handler = URLHandler(client=client,message=message,serialNo=SERIAL_NO)
        url_handler.play()

    def on_media_terminate(self, client, userdata, message):
        try:
            self.terminate_all_active_media()
        except Exception as e:
            logger.error(e)

    def terminate_all_active_media(self):
        logger.info('Terminating all active media')
        subprocess.call(["pkill", "firefox"])
        self.player.terminate()
        publish_message(self.client,"NODE_STATE",{"serialNo":SERIAL_NO,"status":"Idle"})
        
    def start(self):
        try:
            self.client = mqtt.Client(SERIAL_NO)
            self.player = Player(self.client,SERIAL_NO)
            self.client.will_set('NODE_STATE',payload=str(json.dumps({"serialNo":SERIAL_NO,"status":'Offline'})),qos=2)
            self.client.connect(host=MQTT_HOST)
            self.client.on_connect= self.on_mqtt_connect   
            self.client.on_disconnect = self.on_mqtt_disconnect
            self.client.on_message= self.on_mqtt_message
            self.client.message_callback_add(format_topic_name("PLAY_VIDEO"), self.on_media_video)
            self.client.message_callback_add(format_topic_name("DISPLAY_URL"), self.on_media_url)
            self.client.message_callback_add(format_topic_name("PLAY_PLAYLIST"), self.on_media_playlist)
            self.client.message_callback_add(format_topic_name("STOP_MEDIA"), self.on_media_terminate)
            self.client.loop_forever()
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            self.start()

app = APP()

app.start()

