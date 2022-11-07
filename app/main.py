import subprocess
import paho.mqtt.client as mqtt
import ast 
from threading import Thread
from logger.logger import setup_applevel_logger

UNQIUE_ID = "GQNQQRudtv2rfJG"

logger = setup_applevel_logger(__name__)


def display_url(url):
    logger.info(f'URL received: {url}')
    subprocess.call(["pkill", "firefox"])
    subprocess.call(["firefox", f"--kiosk={url}"])

def display_url_handler(message):
    data = str(message.payload.decode("utf-8"))
    newData = ast.literal_eval(data)

    logger.info("Message received: {newData}")

    url = newData["url"]
    if not url:
        logger.error('URL not found')
        return
    t = Thread(target=display_url, args=(url,))
    t.start()

def stop_media_handler():
    logger.info('Terminating all active media')
    subprocess.call(["pkill", "firefox"])
    subprocess.call(["pkill", "mpv"])




def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to broker")
        client.subscribe("DISPLAY_URL")
        client.subscribe("STOP_MEDIA")


    else:
        logger.error("Connection failed")

def on_message(client, userdata, message):
    logger.info("Message received : "  + str(message.payload) + " on " + message.topic)

    if message.topic == "DISPLAY_URL":
        display_url_handler(message)
    
    if message.topic == "STOP_MEDIA":
        stop_media_handler()

mqttBroker = "localhost"

client = mqtt.Client(UNQIUE_ID)
client.on_connect= on_connect    
client.on_message= on_message  
client.connect(mqttBroker,1883)        
      

client.loop_forever()


