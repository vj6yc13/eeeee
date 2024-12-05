import sys
import os
import time
import can
from IPC_Library import IPC_SendPacketWithIPCHeader, TCC_IPC_CMD_CA72_EDUCATION_CAN_DEMO, IPC_IPC_CMD_CA72_EDUCATION_CAN_DEMO_START
from IPC_Library import parse_hex_data

GPIO_EXPORT_PATH = "/sys/class/gpio/export"
GPIO_UNEXPORT_PATH = "/sys/class/gpio/unexport"
GPIO_DIRECTION_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/direction"
GPIO_VALUE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/value"
GPIO_BASE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}"

FREQUENCIES = {
    'C': 261.63,  
    'D': 293.66,  
    'E': 329.63,  
    'F': 349.23,  
    'G': 392.00,  
    'A': 440.00,  
    'B': 493.88,  
    'C5': 523.25  
}

def is_gpio_exported(gpio_number):
    gpio_base_path = GPIO_BASE_PATH_TEMPLATE.format(gpio_number)
    return os.path.exists(gpio_base_path)

def export_gpio(gpio_number):
    if not is_gpio_exported(gpio_number):
        try:
            with open(GPIO_EXPORT_PATH, 'w') as export_file:
                export_file.write(str(gpio_number))
        except IOError as e:
            print(f"Error exporting GPIO {gpio_number}: {e}")
            sys.exit(1)

def unexport_gpio(gpio_number):
    try:
        with open(GPIO_UNEXPORT_PATH, 'w') as unexport_file:
            unexport_file.write(str(gpio_number))
    except IOError as e:
        print(f"Error unexporting GPIO {gpio_number}: {e}")
        sys.exit(1)

def set_gpio_direction(gpio_number, direction):
    gpio_direction_path = GPIO_DIRECTION_PATH_TEMPLATE.format(gpio_number)
    try:
        with open(gpio_direction_path, 'w') as direction_file:
            direction_file.write(direction)
    except IOError as e:
        print(f"Error setting GPIO {gpio_number} direction to {direction}: {e}")
        sys.exit(1)

def set_gpio_value(gpio_number, value):
    gpio_value_path = GPIO_VALUE_PATH_TEMPLATE.format(gpio_number)
    try:
        with open(gpio_value_path, 'w') as value_file:
            value_file.write(str(value))
    except IOError as e:
        print(f"Error setting GPIO {gpio_number} value to {value}: {e}")
        sys.exit(1)

def sendtoCAN(channel, canId, sndDataHex):
    sndData = parse_hex_data(sndDataHex)
    uiLength = len(sndData)
    ret = IPC_SendPacketWithIPCHeader("/dev/tcc_ipc_micom", channel, TCC_IPC_CMD_CA72_EDUCATION_CAN_DEMO, IPC_IPC_CMD_CA72_EDUCATION_CAN_DEMO_START, canId, sndData, uiLength)

def play_tone(gpio_number, frequency, duration, note):
    period = 1.0 / frequency
    half_period = period / 2
    end_time = time.time() + duration

    while time.time() < end_time:
        set_gpio_value(gpio_number, 1)
        time.sleep(half_period)
        set_gpio_value(gpio_number, 0)
        time.sleep(half_period)
        
    # 전송 후 메시지를 CAN에 보내기
    print(f"Playing {note} at {frequency} Hz") 
    sendtoCAN(0, 1, "1")  # CAN 메시지 전송

def listen_for_can_messages():
    # CAN 인터페이스 설정 (예시: 'can0' 사용)
    bus = can.interface.Bus(channel='can0', bustype='socketcan')
    
    while True:
        # CAN 메시지 수신
        message = bus.recv()  # 메시지를 기다리며 수신
        
        if message is not None:
            can_data = message.data.decode('utf-8')  # 수신된 데이터를 문자열로 변환
            print(f"Received CAN message: {can_data}")
            
            if can_data == 'C':
                play_tone(gpio_pin, FREQUENCIES['C'], 0.5, 'C')
            elif can_data == 'D':
                play_tone(gpio_pin, FREQUENCIES['D'], 0.5, 'D')
            elif can_data == 'E':
                play_tone(gpio_pin, FREQUENCIES['E'], 0.5, 'E')
            elif can_data == 'F':
                play_tone(gpio_pin, FREQUENCIES['F'], 0.5, 'F')
            elif can_data == 'G':
                play_tone(gpio_pin, FREQUENCIES['G'], 0.5, 'G')
            elif can_data == 'A':
                play_tone(gpio_pin, FREQUENCIES['A'], 0.5, 'A')
            elif can_data == 'B':
                play_tone(gpio_pin, FREQUENCIES['B'], 0.5, 'B')
            elif can_data == 'C5':
                play_tone(gpio_pin, FREQUENCIES['C5'], 0.5, 'C5')

            time.sleep(0.1)

if __name__ == "__main__":
    gpio_pin = 89  

    try:
        export_gpio(gpio_pin)
        set_gpio_direction(gpio_pin, "out")

        # CAN 메시지를 수신하고 그에 맞는 음을 연주
        listen_for_can_messages()

    except KeyboardInterrupt:
        print("\nOperation stopped by User")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        unexport_gpio(gpio_pin)

    sys.exit(0)
