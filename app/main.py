import subprocess
import paho.mqtt.client as mqtt
import json
from logger.logger import setup_applevel_logger
from dotenv import load_dotenv
from player import Player
from media_handlers.url_handler import URLHandler,URLData
from media_handlers.video_handler import VideoHandler,VideoData
from media_handlers.playlist_handler import PlaylistData, PlaylistHandler
from media_handlers.schedule_handler import ScheduleHandler
import os
import threading
import time
from utils import VIDEOS_DIR
import schedule
from utils import get_data_from_message, publish_message

load_dotenv()

logger = setup_applevel_logger(__name__)


VIDEOS_DIR = VIDEOS_DIR

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

SERIAL_NO = os.getenv('SERIAL_NO')

MQTT_HOST = "test.mosquitto.org"

if not SERIAL_NO:
    logger.error('Serial no not found')
    exit()

def format_topic_name(x): return f'{SERIAL_NO}-{x}'

def job():
    print('yoyoyoy')


 

def job_that_executes_once():
    # Do some work that only needs to happen once...
    print('inside job')
    subprocess.call(["pkill", "firefox"])
    return schedule.CancelJob

class APP:
    def __init__(self,serialNo:str):
        self.client = None 
        self.player = None
        self.serialNo = serialNo
        self.nodeScheduler = schedule.Scheduler()

    
    def on_mqtt_connect(self,client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to broker")
            publish_message(client,"NODE_STATE",{"serialNo":self.serialNo,"status":"Idle"},qos=1)
            client.subscribe(format_topic_name("DISPLAY_URL"))
            client.subscribe(format_topic_name("STOP_MEDIA"))
            client.subscribe(format_topic_name("PLAY_VIDEO"))
            client.subscribe(format_topic_name("PLAY_PLAYLIST"))
            client.subscribe(format_topic_name("SET_SCHEDULE"))
            publish_message(client,"REQUEST_SCHEDULE",{"serialNo":self.serialNo},qos=1)

        else:
            logger.error("Connection failed")
    
    def on_mqtt_disconnect(self,client, userdata, message):
        logger.info('Disconnected from the broker')

    def on_mqtt_message(self,client, userdata, message):
        logger.info("Message received : "  + str(message.payload) + " on " + message.topic)


    def on_media_video(self, client, userdata, message):
        if not self.player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = VideoData(**msgData)
            video_handler = VideoHandler(client=client,data=data,player=self.player,serialNo=self.serialNo,dir=VIDEOS_DIR)
            video_handler.play()
        else:
            logger.error('No msg data')
        # schedule.every(5).seconds.do(video_handler.play)
        # schedule.every().day.at("14:46").do(video_handler.play)
        # schedule.every().day.at("14:47").do(self.player.terminate)
 
    def on_media_playlist(self, client, userdata, message):
        if not self.player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = PlaylistData(**msgData)
            playlist_handler = PlaylistHandler(client=client,data=data,player=self.player,serialNo=self.serialNo,dir=VIDEOS_DIR)
            playlist_handler.play()
        else:
            logger.error('No msg data')

    def on_media_url(self, client, userdata, message):
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = URLData(**msgData)
            url_handler = URLHandler(client=client,data=data,serialNo=self.serialNo)
            url_handler.play()
        else:
            logger.error('No msg data')


    def on_media_terminate(self, client, userdata, message):
        try:
            self.terminate_all_active_media()
        except Exception as e:
            logger.error(e)

    def terminate_all_active_media(self):
        
        logger.info('Terminating all active media')
        subprocess.call(["pkill", "firefox"])
        if self.player:
            self.player.terminate()
        publish_message(self.client,"NODE_STATE",{"serialNo":self.serialNo,"status":"Idle"})

    def on_set_schedule(self, client, userdata, message):
        if not self.player:
            return
        schedule_handler = ScheduleHandler(client=client,message=message,serialNo=self.serialNo,node_schedular=self.nodeScheduler,player=self.player)
        schedule_handler.start()
    def run_pending_jobs(self,interval=1):
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    self.nodeScheduler.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run


    def start(self):
        try:
            self.client = mqtt.Client(self.serialNo)
            self.player = Player(self.client,self.serialNo)
            self.client.will_set('NODE_STATE',payload=str(json.dumps({"serialNo":self.serialNo,"status":'Offline'})),qos=2)
            self.client.connect(host=MQTT_HOST)
            self.client.on_connect= self.on_mqtt_connect   
            self.client.on_disconnect = self.on_mqtt_disconnect
            self.client.on_message= self.on_mqtt_message
            self.client.message_callback_add(format_topic_name("PLAY_VIDEO"), self.on_media_video)
            self.client.message_callback_add(format_topic_name("DISPLAY_URL"), self.on_media_url)
            self.client.message_callback_add(format_topic_name("PLAY_PLAYLIST"), self.on_media_playlist)
            self.client.message_callback_add(format_topic_name("STOP_MEDIA"), self.on_media_terminate)
            self.client.message_callback_add(format_topic_name("SET_SCHEDULE"), self.on_set_schedule)
            self.stop_run_pending_jobs = self.run_pending_jobs()
            self.client.loop_forever()
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            self.start()



app = APP(SERIAL_NO)
app.start()




