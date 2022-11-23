from logger.logger import setup_applevel_logger 
import json
import paho.mqtt.client as mqtt


logger = setup_applevel_logger(__name__)



def publish_message(client:mqtt.Client,topic:str,message):
    try:
        client.publish(topic,str(json.dumps(message)))
        logger.info(f"Published: {message}")
    except Exception as e:
        logger.error(e)