from typing import List
import vlc
from pydantic import BaseModel
from threading import Thread
import paho.mqtt.client as mqtt
from utils import publish_message
from logger.logger import setup_applevel_logger
import datetime
import time
import uuid


class Video(BaseModel):
    id: str
    name: str
    path: str
    duration: int
    size: int


logger = setup_applevel_logger(__name__)


class Player:
    def __init__(self, client: mqtt.Client, serialNo: str):
        self.media_player = vlc.MediaListPlayer(vlc.Instance("--no-xlib"))
        if self.media_player:
            self.player = self.media_player.get_instance()
            self.client = client
            self.serialNo = serialNo
            _player = self.media_player.get_media_player()
            _player.set_fullscreen(True)
            self.media_list = self.player.media_list_new()
            self.playlist = []
            self.playlist_index = None
            self.total_videos = 0
            self.loop = False
            self.playbackID = None
            event_manager = self.media_player.event_manager()
            event_manager.event_attach(
                vlc.EventType.MediaListPlayerPlayed, self.on_player_played)
            event_manager.event_attach(
                vlc.EventType.MediaListPlayerStopped, self.on_player_stopped)
            event_manager.event_attach(
                vlc.EventType.MediaListPlayerNextItemSet, self.on_player_next)
        else:
            logger.error('Media player is None')

    def play(self, playlist: List[Video], loop: bool):
        self.reset_player_conf()
        if not self.media_player:
            return

        if len(playlist) == 0:
            logger.error('playlist is empty')
            return

        self.terminate()
        self.playlist = playlist
        self.loop = loop

        for video in playlist:
            logger.debug(video)
            list_item = self.player.media_new(video.path)
            self.media_list.add_media(list_item)

        self.media_player.set_media_list(self.media_list)

        self.total_videos = self.media_list.count()

        print(f'total video: {self.total_videos}')

        if loop:
            logger.debug('setting loop to true')
            self.media_player.set_playback_mode(vlc.PlaybackMode.loop)
        else:
            logger.debug('setting loop to false')
            self.media_player.set_playback_mode(vlc.PlaybackMode.default)
        self.media_player.play()

        if not loop:
            t1 = Thread(target=self.play_and_exit)
            t1.start()

    # without this function the player get stucked after video is done playing
    # Find a better way to do this

    def play_and_exit(self):
        if not self.media_player:
            return
        time.sleep(1)
        while True:
            if self.media_player.is_playing():
                time.sleep(1)
            else:
                self.media_player.stop()
                break

    def terminate(self):
        if not self.media_player:
            return
        try:
            self.media_player.stop()
        except Exception as e:
            logger.error(e)

    def on_player_stopped(self, event):
        publish_message(self.client, "NODE_STATE", {
                        "serialNo": self.serialNo, "status": "Idle"}, qos=1)
        current_video = self.get_current_video()
        current_playbackID = self.playbackID
        print(current_video)
        print(current_playbackID)
        if current_video and current_playbackID:
            self.send_video_ended_message(
                current_playbackID, current_video.id)

        self.reset_player_conf()
        logger.debug(f'Video Player Stopped')

    def on_player_played(self, event):
        pass

    def on_player_next(self, event):

        if not self.playbackID:
            self.playbackID = uuid.uuid4()
        if self.playlist_index == None:
            self.playlist_index = 0
        else:
            if self.playlist_index < self.total_videos - 1:
                self.playlist_index = self.playlist_index + 1
            else:
                self.playlist_index = 0
        logger.debug(f'current index: {self.playlist_index}')
        current_video = self.get_current_video()
        previous_video = self.get_previous_video()

        if current_video:
            logger.debug(f'Video Next (current): {current_video.name}')
        if previous_video:
            logger.debug(f'Video Next (previous): {previous_video.name}')

        if previous_video and self.playbackID:
            self.send_video_ended_message(
                self.playbackID, previous_video.id)
        if current_video:
            self.send_video_started_message(
                self.playbackID, current_video.id)

    def get_current_video(self) -> Video:
        if len(self.playlist) == 0 or self.playlist_index == None:
            return None
        return self.playlist[self.playlist_index]

    def get_previous_video(self) -> Video:
        if self.total_videos == 0 or self.playlist_index == None:
            return None

        if self.playlist_index == 0 and self.loop == False:
            return None

        if self.playlist_index == 0 and self.loop == True:
            return self.playlist[self.total_videos - 1]

        return self.playlist[self.playlist_index - 1]

    def reset_player_conf(self):
        logger.debug('Resetting player config')
        # release the media list here
        # if self.media_list:
        #     self.media_list.release()
        for i in range(0, self.total_videos):
            self.media_list.remove_index(i)

        self.playlist = []
        self.playlist_index = None
        self.total_videos = 0
        self.loop = False
        self.playbackID = None

    def send_video_started_message(self, playbackID, videoID):
        start_time = datetime.datetime.now()
        serialNo = self.serialNo
        data = {
            'start_time': str(start_time),
            'serialNo': serialNo,
            'videoPlaybackId': str(playbackID),
            'videoId': videoID
        }

        publish_message(self.client, "VIDEO_PLAYBACK", data, qos=1)

    def send_video_ended_message(self, playbackID, videoID):
        end_time = datetime.datetime.now()
        serialNo = self.serialNo
        data = {
            'end_time': str(end_time),
            'serialNo': serialNo,
            'videoPlaybackId': str(playbackID),
            'videoId': videoID
        }

        publish_message(self.client, "VIDEO_PLAYBACK", data, qos=1)
