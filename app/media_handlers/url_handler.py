from pydantic import BaseModel
import json
from logger.logger import setup_applevel_logger
from threading import Thread
import paho.mqtt.client as mqtt
from utils import publish_message
import time
import subprocess
import schedule

logger = setup_applevel_logger(__name__)

def job_that_executes_once():
    # Do some work that only needs to happen once...
    subprocess.call(["pkill", "firefox"])
    return schedule.CancelJob


class URL(BaseModel):
    id: str 
    name: str 
    url: str

class URLData(BaseModel):
    url: URL 
    duration: int

class URLHandler:
    def __init__(self,client:mqtt.Client,data:URLData,serialNo:str):
        self.client = client
        self.data = data
        self.searialNo = serialNo

    def __del__(self):
        logger.debug('Destructor called, URLHandler deleted.')

    def play(self):
        # if the duration is less than 0 we will keep the browser running for infinite time
        if self.data.duration > 0:
            schedule.every(self.data.duration).seconds.do(job_that_executes_once)
        t1 = Thread(target=self.open_browser)
        t1.start()
        # schedule.idle_seconds()

        # if self.data.seconds > 0:
        #     t2 = Thread(target=self.close_browser,args=(self.data.seconds,))
        #     t2.start()

    def open_browser(self):
        url_to_open = self.data.url.url
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Playing","playingData":{"type":"Url","mediaId":self.data.url.id}})
        logger.info(f'Opening browser with link : {url_to_open}')
        subprocess.call(["firefox", f"--kiosk={url_to_open}"])
     
    # need fix: it will close the browser even if another url is playing
    def close_browser(self,seconds):
        time.sleep(seconds)
        subprocess.call(["pkill", "firefox"])
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Idle"})

