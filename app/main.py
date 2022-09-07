import socketio
import time
from logger.logger import setup_applevel_logger


logger = setup_applevel_logger(__name__)

sio = socketio.Client()

connected = False


@sio.event
def connect():
    logger.info('Connection establised')


@sio.event
def my_message(data):
    print("message received with ", data)
    sio.emit("my response", {"response": "my response"})

@sio.event
def upload_video(data):
    filename = data['filename']
    try:
        with open(filename, "wb") as f:
            f.write(data['file_content'])
        logger.info(f'{filename} saved')
    except Exception as e:
        logger.error(e)



@sio.event
def disconnect():
    logger.info('Disconnected from server')


while not connected:
    try:
        sio.connect("http://192.168.29.233:3000")
        sio.wait()
        connected = True
    except Exception as ex:
        logger.error(
            f"Failed to establish initial connnection to server: {type(ex).__name__}"
        )
        time.sleep(2)
