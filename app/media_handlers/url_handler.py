from pydantic import BaseModel
import json
from logger.logger import setup_applevel_logger
from threading import Thread
import paho.mqtt.client as mqtt
from utils import publish_message
import time
import subprocess

logger = setup_applevel_logger(__name__)

class URLData(BaseModel):
    id: str
    url: str 
    seconds: int

class URLHandler:
    def __init__(self,client:mqtt.Client,message,serialNo:str):
        self.client = client
        self.message = message
        self.searialNo = serialNo
        dataStr = str(message.payload.decode("utf-8"))
        data = json.loads(dataStr)

        try:
            self.context_data = URLData(**data)
        except Exception as e:
            logger.error(e)

    def play(self):
        t1 = Thread(target=self.open_browser)
        t1.start()

        if self.context_data.seconds > 0:
            t2 = Thread(target=self.close_browser,args=(self.context_data.seconds,))
            t2.start()
   


    def open_browser(self):
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Playing","playingData":{"type":"Url","mediaId":self.context_data.id}})
        logger.info(f'Opening browser with link : {self.context_data.url}')
        subprocess.call(["firefox", f"--kiosk={self.context_data.url}"])
     
    # need fix: it will close the browser even if another url is playing
    def close_browser(self,seconds):
        time.sleep(seconds)
        subprocess.call(["pkill", "firefox"])
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Idle"})

