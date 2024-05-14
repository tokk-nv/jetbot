import time
import traitlets
from traitlets.config.configurable import SingletonConfigurable
from Adafruit_MotorHAT import Adafruit_MotorHAT
from .motor import Motor
from smbus2 import SMBus

I2C_EEPROM_BUS = [0, 1, 2, 7]
MODULE_I2CBUS_TABLE = {
    'p3767-0005': 7, #'NVIDIA Jetson Orin Nano (Developer kit)',
    'p3767-0004': 7, #'NVIDIA Jetson Orin Nano (4GB ram)',
    'p3767-0003': 7, #'NVIDIA Jetson Orin Nano (8GB ram)',
    'p3767-0001': 7, #'NVIDIA Jetson Orin NX (8GB ram)',
    'p3767-0000': 7, #'NVIDIA Jetson Orin NX (16GB ram)',
    'p3701-0005': 7, #'NVIDIA Jetson AGX Orin (64GB ram)',
    'p3701-0004': 7, #'NVIDIA Jetson AGX Orin (32GB ram)',
    'p3701-0002': 7, #'NVIDIA Jetson IGX Orin (Developer kit)',
    'p3701-0000': 7, #'NVIDIA Jetson AGX Orin',
    'p3668-0003': 8, #'NVIDIA Jetson Xavier NX (16GB ram)',
    'p3668-0001': 8, #'NVIDIA Jetson Xavier NX',
    'p3668-0000': 8, #'NVIDIA Jetson Xavier NX (Developer kit)',
    'p2888-0008': 8, #'NVIDIA Jetson AGX Xavier Industrial (32 GB ram)',
    'p2888-0006': 8, #'NVIDIA Jetson AGX Xavier (8 GB ram)',
    'p2888-0005': 8, #'NVIDIA Jetson AGX Xavier (64 GB ram)',
    'p2888-0004': 8, #'NVIDIA Jetson AGX Xavier (32 GB ram)',
    'p2888-0003': 8, #'NVIDIA Jetson AGX Xavier (32 GB ram)',
    'p2888-0001': 8, #'NVIDIA Jetson AGX Xavier (16 GB ram)',
    'p3448-0003': 1, #'NVIDIA Jetson Nano (2 GB ram)',
    'p3448-0002': 1, #'NVIDIA Jetson Nano module (16Gb eMMC)',
    'p3448-0000': 1, #'NVIDIA Jetson Nano (4 GB ram)',
    'p3636-0001': 1, #'NVIDIA Jetson TX2 NX',
    'p3509-0000': 1, #'NVIDIA Jetson TX2 NX',
    'p3489-0888': 1, #'NVIDIA Jetson TX2 (4 GB ram)',
    'p3489-0000': 1, #'NVIDIA Jetson TX2i',
    'p3310-1000': 1, #'NVIDIA Jetson TX2',
    'p2180-1000': 0, #'NVIDIA Jetson TX1',
    'r375-0001': 1, #'NVIDIA Jetson TK1', https://jetsonhacks.com/2015/10/25/4-character-7-segment-led-over-i2c-nvidia-jetson-tk1/
    'p3904-0000': 99, #'NVIDIA Clara AGX',
    # Other modules
    'p2595-0000-A0': 99 #'Nintendo Switch'
}

def get_part_number():
    part_number = ''
    jetson_part_number = ''
    # Find 699-level part number from EEPROM and extract P-number
    for bus_number in I2C_EEPROM_BUS:
        try:
            bus = SMBus(bus_number)
            part_number = bus.read_i2c_block_data(0x50, 20, 29)
            part_number = ''.join(chr(i) for i in part_number).rstrip('\x00')
            # print(part_number)
            board_id = part_number[5:9]
            sku = part_number[10:14]
            jetson_part_number = "p{board_id}-{sku}".format(board_id=board_id, sku=sku)
            return part_number, jetson_part_number
        except (IOError, OSError):
            # print("Error I2C bus: {bus_number}".format(bus_number=bus_number))
            pass
    return part_number, jetson_part_number

class Robot(SingletonConfigurable):
    
    left_motor = traitlets.Instance(Motor)
    right_motor = traitlets.Instance(Motor)

    # I2C bus number detection
    part_number, jetson_part_number = get_part_number()
    i2c_bus_number = MODULE_I2CBUS_TABLE.get(jetson_part_number)
    if not i2c_bus_number:
        i2c_bus_number = 7  # Default: I2C bus 7 for Jetson AGX Orin

    # config
    i2c_bus = traitlets.Integer(default_value=i2c_bus_number).tag(config=True)
    left_motor_channel = traitlets.Integer(default_value=1).tag(config=True)
    left_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)
    right_motor_channel = traitlets.Integer(default_value=2).tag(config=True)
    right_motor_alpha = traitlets.Float(default_value=1.0).tag(config=True)
    
    def __init__(self, *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self.motor_driver = Adafruit_MotorHAT(i2c_bus=self.i2c_bus)
        self.left_motor = Motor(self.motor_driver, channel=self.left_motor_channel, alpha=self.left_motor_alpha)
        self.right_motor = Motor(self.motor_driver, channel=self.right_motor_channel, alpha=self.right_motor_alpha)
        
    def set_motors(self, left_speed, right_speed):
        self.left_motor.value = left_speed
        self.right_motor.value = right_speed
        
    def forward(self, speed=1.0, duration=None):
        self.left_motor.value = speed
        self.right_motor.value = speed

    def backward(self, speed=1.0):
        self.left_motor.value = -speed
        self.right_motor.value = -speed

    def left(self, speed=1.0):
        self.left_motor.value = -speed
        self.right_motor.value = speed

    def right(self, speed=1.0):
        self.left_motor.value = speed
        self.right_motor.value = -speed

    def stop(self):
        self.left_motor.value = 0
        self.right_motor.value = 0