import socketio
import time

sio = socketio.Client()

connected = False

@sio.event
def connect():
    print('connection established')


@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})


@sio.event
def disconnect():
    print('disconnected from server')



while not connected:
    try:
        sio.connect("http://localhost:3000")
        sio.wait()
        print("Socket established")
        connected = True
    except Exception as ex:
        print("Failed to establish initial connnection to server:", type(ex).__name__)
        time.sleep(2)