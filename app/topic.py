from enum import Enum
 
class Topic(Enum):
    SPRING = 'SPRING'
    SUMMER = 'SUMMER'
    AUTUMN = 'AUTUMN'
    WINTER = 'WINTER'
    
    def __str__(self) -> str:
        return self.value


class MQTT_TOPIC():
    def __init__(self,serial_no:str):
        self.serial_no = serial_no

