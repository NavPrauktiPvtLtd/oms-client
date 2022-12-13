import json
from datetime import datetime
from pydantic import BaseModel
import paho.mqtt.client as mqtt
from typing import List, Optional
from media_handlers.url_handler import URL
from media_handlers.video_handler import Video
from logger.logger import setup_applevel_logger
from media_handlers.playlist_handler import PlaylistData 

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
    def __init__(self,client:mqtt.Client,message,serialNo:str):
        self.client = client 
        self.message = message 
        self.serialNo = serialNo
        dataStr = str(message.payload.decode("utf-8"))
        data = json.loads(dataStr)
        try:
            self.context_data = ScheduleData(**data)
            # print(self.context_data)
        except Exception as e:
            logger.error(e)

    # def schedule_video(start_time:str,end_time:str):


    def start(self):
        for schedule_item in self.context_data.ScheduleItem:
            start_time = schedule_item.start_time
            end_time = schedule_item.end_time 


