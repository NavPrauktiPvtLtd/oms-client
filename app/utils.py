from logger.logger import setup_applevel_logger 
import json
import paho.mqtt.client as mqtt

logger = setup_applevel_logger(__name__)

def publish_message(client:mqtt.Client,topic:str,message,qos=0):
    if not client:
        logger.error('Mqtt client is None')
        return
    try:
        client.publish(topic,str(json.dumps(message)),qos=qos)
        logger.info(f"Published: {message}")
    except Exception as e:
        logger.error(e)