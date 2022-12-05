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
        print(self.context_data.seconds)
        schedule.every(self.context_data.seconds).seconds.do(job_that_executes_once)
        t1 = Thread(target=self.open_browser)
        t1.start()
        # schedule.idle_seconds()

        # if self.context_data.seconds > 0:
        #     t2 = Thread(target=self.close_browser,args=(self.context_data.seconds,))
        #     t2.start()

    def open_browser(self):
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Playing","playingData":{"type":"Url","mediaId":self.context_data.id}})
        logger.info(f'Opening browser with link : {self.context_data.url}')
        subprocess.call(["firefox", f"--kiosk={self.context_data.url}"])
     
    # need fix: it will close the browser even if another url is playing
    def close_browser(self,seconds):
        time.sleep(seconds)
        subprocess.call(["pkill", "firefox"])
        publish_message(self.client,"NODE_STATE",{"serialNo":self.searialNo,"status":"Idle"})

