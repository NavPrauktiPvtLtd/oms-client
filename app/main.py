import os
import time
import json
import schedule
import threading
import subprocess
from player import Player
from playlist_player import PlaylistPlayer
from utils import VIDEOS_DIR, VIDEOS_PLAYBACK_HISTORY_PATH, check_and_create_file
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from topic import Topic
from logger.logger import setup_applevel_logger
from utils import get_data_from_message, publish_message
from media_handlers.url_handler import URLHandler, URLData
from media_handlers.video_handler import VideoHandler, VideoData
from media_handlers.playlist_handler import PlaylistData, PlaylistHandler
from media_handlers.schedule_handler import ScheduleHandler, ScheduleData

load_dotenv()

logger = setup_applevel_logger(__name__)


VIDEOS_DIR = VIDEOS_DIR


check_and_create_file(
    file_path=VIDEOS_PLAYBACK_HISTORY_PATH, initial_content='{}')

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)


SERIAL_NO = os.getenv('SERIAL_NO')

MQTT_HOST = os.getenv('MQTT_HOST')

if not SERIAL_NO:
    logger.error('Serial Number not found')
    exit()

if not MQTT_HOST:
    logger.error('MQTT host not found')
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
    def __init__(self, serialNo: str, mqtt_host: str):
        self.client = None
        self.player = None
        self.playlist_player = None
        self.serialNo = serialNo
        self.nodeScheduler = schedule.Scheduler()
        self.scheduleId = None
        self.mqtt_host = mqtt_host

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to broker")
            publish_message(client, Topic.NODE_STATE, {
                            "serialNo": self.serialNo, "status": "Idle"}, qos=1)
            client.subscribe(format_topic_name(Topic.DISPLAY_URL))
            client.subscribe(format_topic_name(Topic.STOP_MEDIA))
            client.subscribe(format_topic_name(Topic.PLAY_VIDEO))
            client.subscribe(format_topic_name(Topic.PLAY_PLAYLIST))
            client.subscribe(format_topic_name(Topic.SET_SCHEDULE))
            publish_message(client, Topic.REQUEST_SCHEDULE, {
                            "serialNo": self.serialNo}, qos=1)

        else:
            logger.error("Connection failed")

    def on_mqtt_disconnect(self, client, userdata, message):
        logger.info('Disconnected from the broker')

    def on_mqtt_message(self, client, userdata, message):
        logger.info("Message received : " +
                    str(message.payload) + " on " + message.topic)

    def on_media_video(self, client, userdata, message):
        if not self.player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = VideoData(**msgData)
            video_handler = VideoHandler(
                client=client, data=data, player=self.player, serialNo=self.serialNo, dir=VIDEOS_DIR)
            video_handler.play()
        else:
            logger.error('No msg data in set_video message')

    def on_media_playlist(self, client, userdata, message):
        if not self.playlist_player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = PlaylistData(**msgData)
            playlist_handler = PlaylistHandler(
                client=client, data=data, player=self.playlist_player, serialNo=self.serialNo, dir=VIDEOS_DIR)
            playlist_handler.play()
        else:
            logger.error('No msg data in set_playlist message')

    def on_media_url(self, client, userdata, message):
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = URLData(**msgData)
            url_handler = URLHandler(
                client=client, data=data, serialNo=self.serialNo)
            url_handler.play()
        else:
            logger.error('No msg data in set_url message')

    def on_media_terminate(self, client, userdata, message):
        try:
            self.terminate_all_active_media()
        except Exception as e:
            logger.error(e)

    def request_default_video(self):
        publish_message(self.client, Topic.REQUEST_DEFAULT_VIDEO, {
            "serialNo": self.serialNo}, qos=1)

    def on_set_default_video(self, client, userdata, message):
        if not self.player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = VideoData(**msgData)
            video_handler = VideoHandler(
                client=client, data=data, player=self.player, serialNo=self.serialNo, dir=VIDEOS_DIR)
            video_handler.play()
        else:
            logger.error('No msg data in set_video message')

    def terminate_all_active_media(self):
        logger.info('Terminating all active media')
        subprocess.call(["pkill", "firefox"])
        if self.player:
            self.player.terminate()
        if self.playlist_player:
            self.playlist_player.terminate()
        publish_message(self.client, "NODE_STATE", {
                        "serialNo": self.serialNo, "status": "Idle"})

    def on_set_schedule(self, client, userdata, message):
        if not self.player or not self.playlist_player:
            return
        logger.info(msg='new schedule received')
        # IMP: it might cause problem with browser close schedules
        logger.info(msg='cleared previous schedule')
        msgData = get_data_from_message(message)
        if msgData:
            self.nodeScheduler.clear()
            data = ScheduleData(**msgData)

            # check if we are updating the current schedule
            if self.scheduleId != data.id:
                self.terminate_all_active_media()

            schedule_handler = ScheduleHandler(
                client=client, data=data, serialNo=self.serialNo, node_schedular=self.nodeScheduler, player=self.player, playlist_player=self.playlist_player)
            schedule_handler.start()
        else:
            logger.error('No msg data in set_schedule msg')

    def run_pending_jobs(self, interval=1):
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
            self.player = Player(self.client, self.serialNo)
            self.playlist_player = PlaylistPlayer(self.client, self.serialNo)
            self.client.will_set(Topic.NODE_STATE, payload=str(json.dumps(
                {"serialNo": self.serialNo, "status": 'Offline'})), qos=2)
            self.client.connect(host=self.mqtt_host)
            self.client.on_connect = self.on_mqtt_connect
            self.client.on_disconnect = self.on_mqtt_disconnect
            self.client.on_message = self.on_mqtt_message
            self.client.message_callback_add(
                format_topic_name(Topic.PLAY_VIDEO), self.on_media_video)
            self.client.message_callback_add(
                format_topic_name(Topic.DISPLAY_URL), self.on_media_url)
            self.client.message_callback_add(format_topic_name(
                Topic.PLAY_PLAYLIST), self.on_media_playlist)
            self.client.message_callback_add(
                format_topic_name(Topic.STOP_MEDIA), self.on_media_terminate)
            self.client.message_callback_add(
                format_topic_name(Topic.SET_SCHEDULE), self.on_set_schedule)
            self.stop_run_pending_jobs = self.run_pending_jobs()
            self.client.loop_forever()
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            self.start()


app = APP(SERIAL_NO, MQTT_HOST)
app.start()
