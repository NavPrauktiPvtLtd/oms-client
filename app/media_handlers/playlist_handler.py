from pydantic import BaseModel
import json
from logger.logger import setup_applevel_logger
import paho.mqtt.client as mqtt
from utils import  publish_message
from player import Player
import os
from typing import List, Optional
import requests
from media_handlers.video_handler import Video


logger = setup_applevel_logger(__name__)


class PlaylistData(BaseModel):
    id: str 
    name: str 
    videos: List[Video]
    loop: Optional[bool]

class PlaylistHandler:
    def __init__(self,client:mqtt.Client,message,player:Player,serialNo:str,dir:str):
        self.client = client
        self.message = message
        self.player = player
        self.dir = dir 
        self.searialNo = serialNo
        dataStr = str(message.payload.decode("utf-8"))
        data = json.loads(dataStr)

        try:
            self.context_data = PlaylistData(**data)
        except Exception as e:
            logger.error(e)

    def play(self):
        id = self.context_data.id
        name = self.context_data.name
        videos = self.context_data.videos
        loop = False 
        if(self.context_data.loop):
            loop = True

        filepath = self.file_path(name)

        for video in videos:
            filepath = self.file_path(video.name)
            if not os.path.exists(filepath):
                self.download_video_from_url(video.path,filepath)
                
        self.play_playlist(videos,loop,id)


    def download_video_from_url(self,url:str,path:str):
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Processing"})
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Idle"})

    def play_playlist(self,videos:List[Video],loop:bool,id:str):
        playlist_paths = []

        for video in videos:
            filepath = self.file_path(video.name)
            playlist_paths.append(filepath)

        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Playing","playingData":{"type":"VideoList","mediaId":id}})
        self.player.play(playlist_paths,loop)

    def file_path(self,x): return os.path.join(self.dir, x)
