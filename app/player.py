import vlc
from threading import Thread
import paho.mqtt.client as mqtt
from utils import publish_message
from logger.logger import setup_applevel_logger
import time

logger = setup_applevel_logger(__name__)

class Player:
    def __init__(self,client:mqtt.Client,serialNo:str):
        self.media_player = vlc.MediaListPlayer(vlc.Instance())
        self.player = self.media_player.get_instance()
        self.client = client
        self.serialNo = serialNo
        _player = self.media_player.get_media_player()
        _player.set_fullscreen(True)

    def play(self,playlist:list,loop:bool):
        self.terminate()
        media_list = self.player.media_list_new()

        for item in playlist:
            logger.debug(item)
            list_item = self.player.media_new(item)
            media_list.add_media(list_item)

        self.media_player.set_media_list(media_list)

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

        # def cb(event):
        #     logger.debug('inside callback function')



        # event_manager = self.media_player.event_manager()
        # event_manager.event_attach(vlc.EventType.MediaListPlayerPlayed, cb)


    # without this function the player get stucked after video is done playing
    # Find a better way to do this
    def play_and_exit(self):
        time.sleep(1)
        while True:
            if self.media_player.is_playing():
                time.sleep(1)
            else:
                self.media_player.stop()
                break
        publish_message(self.client,"NODE_STATE",{"serialNo":self.serialNo,"status":"Idle"},qos=1)
        
    def terminate(self):
        try:
            self.media_player.stop()
        except Exception as e:
            logger.error(e)






     