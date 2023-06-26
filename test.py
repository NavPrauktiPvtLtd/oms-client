import os
from dotenv import load_dotenv

load_dotenv()

# this value is in bytes
MAX_VIDEO_STORAGE_SIZE = os.environ['SERIAL_NO']

print(MAX_VIDEO_STORAGE_SIZE)
