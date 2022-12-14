from pydantic import BaseModel
from logger.logger import setup_applevel_logger
import paho.mqtt.client as mqtt
from utils import publish_message
from player import Player
from threading import Thread
import os
import requests

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
    def __init__(self,client:mqtt.Client,data:VideoData,player:Player,serialNo:str,dir:str):
        self.client = client
        self.player = player
        self.dir = dir 
        self.searialNo = serialNo
        self.data = data


    def play(self):
        id = self.data.video.id
        name = self.data.video.name
        url = self.data.video.path
        loop = self.data.loop

        filepath = self.file_path(name)

        if os.path.exists(filepath):
            logger.info('video already exists skipping download')
            self.play_video(filepath,loop,id)
        else:
            logger.info('downloading video')
            self.download_video_from_url(url,filepath)
            self.play_video(filepath,loop,id)

    def file_path(self,x): return os.path.join(self.dir, x)

    def download_video_from_url(self,url,path):
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Processing"})
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)

    def play_video(self,filepath,loop,id):
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Playing","playingData":{"type":"Video","mediaId":id}})
        t1 = Thread(target=self.player.play,args=([filepath],loop,))
        t1.start()
