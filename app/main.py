import os
from pathlib import Path
import socketio
import time
from logger.logger import setup_applevel_logger


BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parents[0])
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")


def file_path(x): return os.path.join(VIDEOS_DIR, x)

if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)


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
    filename = file_path(data['filename'])
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
        sio.connect("http://127.0.0.0:3000")
        sio.wait()
        connected = True
    except Exception as ex:
        logger.error(
            f"Failed to establish initial connnection to server: {type(ex).__name__}"
        )
        time.sleep(2)
