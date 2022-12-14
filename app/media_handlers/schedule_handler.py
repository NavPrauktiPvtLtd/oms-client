import json
import schedule
from datetime import datetime
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from typing import List, Optional
from utils import VIDEOS_DIR
from media_handlers.url_handler import URL,URLData,URLHandler
from media_handlers.video_handler import Video, VideoHandler,VideoData
from logger.logger import setup_applevel_logger
from media_handlers.playlist_handler import PlaylistData, PlaylistHandler 
from player import Player




logger = setup_applevel_logger(__name__)


class ScheduleItemData(BaseModel):
    start_time: str
    end_time: str 
    loop: Optional[bool]   
    duration: Optional[int] 
    url: Optional[URL]
    video: Optional[Video]
    playlist: Optional[PlaylistData] 

class ScheduleData(BaseModel):
    id: str 
    name: str
    is_active: bool
    createdAt: datetime
    updatedAt: datetime
    nodeId: str 
    ScheduleItem: List[ScheduleItemData]
    

class ScheduleHandler:
    def __init__(self,client:mqtt.Client,message,serialNo:str,node_schedular:schedule.Scheduler,player:Player):
        self.client = client 
        self.message = message 
        self.serialNo = serialNo
        self.player = player
        self.node_schedular = node_schedular
        dataStr = str(message.payload.decode("utf-8"))
        data = json.loads(dataStr)
        try:
            self.context_data = ScheduleData(**data)
        except Exception as e:
            logger.error(e)

    def __del__(self):
        logger.debug('Destructor called, ScheduleHandler deleted.')

    def schedule_video(self,start_time:str,end_time:str,video:Video,loop:bool|None):
        logger.debug(f'Schedule created: start-time - {start_time} and end-time - {end_time} | media-type: video | media = {video.name}')
        if not loop:
            loop = False
        video_data = VideoData(video=video,loop=loop)
        video_handler = VideoHandler(client=self.client,data=video_data,player=self.player,serialNo=self.serialNo,dir=VIDEOS_DIR)

        self.node_schedular.every().day.at(start_time).do(video_handler.play)

    def schedule_url(self,start_time:str,end_time:str,url:URL):
        logger.debug(f'Schedule created: start-time - {start_time} and end-time - {end_time} | media-type: url | media = {url.name}')
        url_data =URLData(url=url,duration=0)
        url_handler = URLHandler(client=self.client,data=url_data,serialNo=self.serialNo)

        self.node_schedular.every().day.at(start_time).do(url_handler.play)

    def schedule_playlist(self,start_time:str,end_time:str,playlist_data:PlaylistData,loop:bool|None):
        logger.debug(f'Schedule created: start-time - {start_time} and end-time - {end_time} | media-type: playlist | media = {playlist_data.name}')
        if not loop:
            loop = False
  
        playlist_handler = PlaylistHandler(client=self.client,data=playlist_data,player=self.player,serialNo=self.serialNo,dir=VIDEOS_DIR)
        self.node_schedular.every().day.at(start_time).do(playlist_handler.play)

    def start(self):
        for schedule_item in self.context_data.ScheduleItem:
            start_time = schedule_item.start_time
            end_time = schedule_item.end_time
            if schedule_item.video:
                self.schedule_video(start_time=start_time,end_time=end_time,video=schedule_item.video,loop=schedule_item.loop) 

            if schedule_item.playlist:
                self.schedule_playlist(start_time=start_time,end_time=end_time,playlist_data=schedule_item.playlist,loop=schedule_item.loop)

            if schedule_item.url:
                self.schedule_url(start_time=start_time,end_time=end_time,url=schedule_item.url)


