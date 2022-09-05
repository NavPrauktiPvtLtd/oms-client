import socketio
import time
from logger.logger import setup_applevel_logger


logger = setup_applevel_logger(__name__)

sio = socketio.Client()

connected = False


@sio.event
def connect():
    print("connection established")


@sio.event
def my_message(data):
    print("message received with ", data)
    sio.emit("my response", {"response": "my response"})


@sio.event
def disconnect():
    print("disconnected from server")


while not connected:
    try:
        sio.connect("http://192.168.29.116:3000")
        sio.wait()
        print("Socket established")
        connected = True
    except Exception as ex:
        logger.error(
            f"Failed to establish initial connnection to server: {type(ex).__name__}"
        )
        time.sleep(2)
