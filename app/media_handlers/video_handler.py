from pydantic import BaseModel
from logger.logger import setup_applevel_logger
import paho.mqtt.client as mqtt
from utils import publish_message, VIDEOS_PLAYBACK_HISTORY_PATH, MAX_VIDEO_STORAGE_SIZE
from player import Player
from threading import Thread
from topic import Topic
import os
import requests
from .video_memory_manager import VideoMemoryManager

logger = setup_applevel_logger(__name__)


class Video(BaseModel):
    id: str
    name: str
    path: str
    duration: int
    size: int


class VideoData(BaseModel):
    video: Video
    loop: bool


class VideoHandler:
    def __init__(self, client: mqtt.Client, data: VideoData, player: Player, serialNo: str, dir: str):
        self.client = client
        self.player = player
        self.dir = dir
        self.searialNo = serialNo
        self.data = data

    def __del__(self):
        logger.debug('Destructor called, VideoHandler deleted.')

    def play(self):
        id = self.data.video.id
        name = self.data.video.name
        url = self.data.video.path
        size = self.data.video.size
        loop = self.data.loop

        filepath = self.file_path(name)

        self.data.video.path = filepath

        memory_manager = VideoMemoryManager(
            VIDEOS_PLAYBACK_HISTORY_PATH, MAX_VIDEO_STORAGE_SIZE)

        # check if there is

        if os.path.exists(filepath):
            logger.info('video already exists skipping download')
            memory_manager.update_last_played(name)
            self.play_video()
        else:
            logger.info('downloading video')
            if not memory_manager.is_enough_space(size):
                memory_manager.make_space(size)
            memory_manager.insert_new_video(name, size)
            self.download_video_from_url(url, filepath)
            self.play_video()

    def file_path(self, x): return os.path.join(self.dir, x)

    def download_video_from_url(self, url, path):
        publish_message(self.client, Topic.NODE_STATE, {
                        "serialNo": self.searialNo, "status": "Processing"})
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)

    def play_video(self):
        publish_message(self.client, Topic.NODE_STATE, {"serialNo": self.searialNo, "status": "Playing", "playingData": {
                        "type": "Video", "mediaId": self.data.video.id}})
        logger.debug(self.data.video)
        t1 = Thread(target=self.player.play, args=(
            [self.data.video], self.data.loop,))
        t1.start()
