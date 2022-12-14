import os
import time
import json
import schedule
import threading
import subprocess
from utils import VIDEOS_DIR
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from logger.logger import setup_applevel_logger
from utils import get_data_from_message, publish_message
from media_handlers.url_handler import URLHandler, URLData
from media_handlers.video_handler import VideoHandler, VideoData
from media_handlers.playlist_handler import PlaylistData, PlaylistHandler
from media_handlers.schedule_handler import ScheduleHandler, ScheduleData
import vlc
from threading import Thread

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


def file_path(x): return os.path.join(VIDEOS_DIR, x)


class APP:
    def __init__(self, serialNo: str):
        self.client = None
        self.serialNo = serialNo
        self.nodeScheduler = schedule.Scheduler()
        self.scheduleId = None
        self.player = self.init_player()

    def init_player(self):
        media_player = vlc.MediaListPlayer(vlc.Instance())
        if media_player:
            player = media_player.get_instance()
            _player = media_player.get_media_player()
            _player.set_fullscreen(True)
            return media_player

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to broker")
            publish_message(client, "NODE_STATE", {
                            "serialNo": self.serialNo, "status": "Idle"}, qos=1)
            client.subscribe(format_topic_name("DISPLAY_URL"))
            client.subscribe(format_topic_name("STOP_MEDIA"))
            client.subscribe(format_topic_name("PLAY_VIDEO"))
            client.subscribe(format_topic_name("PLAY_PLAYLIST"))
            client.subscribe(format_topic_name("SET_SCHEDULE"))
            publish_message(client, "REQUEST_SCHEDULE", {
                            "serialNo": self.serialNo}, qos=1)

        else:
            logger.error("Connection failed")

    def on_mqtt_disconnect(self, client, userdata, message):
        logger.info('Disconnected from the broker')

    def on_mqtt_message(self, client, userdata, message):
        logger.info("Message received : " +
                    str(message.payload) + " on " + message.topic)

    def terminate_video_player(self):
        if not self.player:
            return
        try:
            self.player.stop()
        except Exception as e:
            logger.error(e)

    def vlc_play_video(self, filepath: str, loop: bool, id: str):
        if not self.player:
            logger.error('Media player not found')
            return
        self.terminate_video_player()
        player_instance = self.player.get_instance()
        media_list = player_instance.media_list_new()

        list_item = player_instance.media_new(filepath)
        media_list.add_media(list_item)

        self.player.set_media_list(media_list)

        if loop:
            logger.debug('setting loop to true')
            self.player.set_playback_mode(vlc.PlaybackMode.loop)
        else:
            logger.debug('setting loop to false')
            self.player.set_playback_mode(vlc.PlaybackMode.default)

        self.player.play()

    def play_video(self, filepath: str, loop: bool, id: str):
        publish_message(self.client, "NODE_STATE", {
                        "serialNo": self.serialNo, "status": "Playing", "playingData": {"type": "Video", "mediaId": id}})
        t1 = Thread(target=self.vlc_play_video, args=([filepath], loop, id,))
        t1.start()

    def video_handler(self, data: VideoData):
        id = data.video.id
        name = data.video.name
        url = data.video.path
        loop = data.loop

        filepath = file_path(name)

        if os.path.exists(filepath):
            logger.info('video already exists skipping download')
            self.play_video(filepath, loop, id)
        else:
            logger.info('downloading video')
            self.download_video_from_url(url, filepath)
            self.play_video(filepath, loop, id)

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
        if not self.player:
            return
        self.terminate_all_active_media()
        msgData = get_data_from_message(message)
        if msgData:
            data = PlaylistData(**msgData)
            playlist_handler = PlaylistHandler(
                client=client, data=data, player=self.player, serialNo=self.serialNo, dir=VIDEOS_DIR)
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

    def terminate_all_active_media(self):
        logger.info('Terminating all active media')
        subprocess.call(["pkill", "firefox"])
        if self.player:
            self.player.terminate()
        publish_message(self.client, "NODE_STATE", {
                        "serialNo": self.serialNo, "status": "Idle"})

    def on_set_schedule(self, client, userdata, message):
        if not self.player:
            return
        logger.info(msg='new schedule received')
        # IMP: it might cause problem with browser close schedules
        self.nodeScheduler.clear()
        logger.info(msg='cleared previous schedule')
        msgData = get_data_from_message(message)
        if msgData:
            data = ScheduleData(**msgData)

            # check if we are updating the current schedule
            if self.scheduleId != data.id:
                self.terminate_all_active_media()

            schedule_handler = ScheduleHandler(
                client=client, data=data, serialNo=self.serialNo, node_schedular=self.nodeScheduler, player=self.player)
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
            self.client.will_set('NODE_STATE', payload=str(json.dumps(
                {"serialNo": self.serialNo, "status": 'Offline'})), qos=2)
            self.client.connect(host=MQTT_HOST)
            self.client.on_connect = self.on_mqtt_connect
            self.client.on_disconnect = self.on_mqtt_disconnect
            self.client.on_message = self.on_mqtt_message
            self.client.message_callback_add(
                format_topic_name("PLAY_VIDEO"), self.on_media_video)
            self.client.message_callback_add(
                format_topic_name("DISPLAY_URL"), self.on_media_url)
            self.client.message_callback_add(format_topic_name(
                "PLAY_PLAYLIST"), self.on_media_playlist)
            self.client.message_callback_add(
                format_topic_name("STOP_MEDIA"), self.on_media_terminate)
            self.client.message_callback_add(
                format_topic_name("SET_SCHEDULE"), self.on_set_schedule)
            self.stop_run_pending_jobs = self.run_pending_jobs()
            self.client.loop_forever()
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            self.start()


app = APP(SERIAL_NO)
app.start()
