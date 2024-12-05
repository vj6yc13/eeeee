import sys
import os
import time
import threading

GPIO_EXPORT_PATH = "/sys/class/gpio/export"
GPIO_UNEXPORT_PATH = "/sys/class/gpio/unexport"
GPIO_DIRECTION_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/direction"
GPIO_VALUE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/value"
GPIO_BASE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}"

FREQUENCIES = {
    1: 261.63,  # C
    2: 293.66,  # D
    3: 329.63,  # E
    4: 349.23,  # F
    5: 392.00,  # G
    6: 440.00,  # A
    7: 493.88,  # B
    8: 523.25   # C5
}

received_pucData = []  # IPC에서 수신한 데이터 저장

# GPIO 유틸리티 함수
def is_gpio_exported(gpio_number):
    gpio_base_path = GPIO_BASE_PATH_TEMPLATE.format(gpio_number)
    return os.path.exists(gpio_base_path)

def export_gpio(gpio_number):
    if not is_gpio_exported(gpio_number):
        with open(GPIO_EXPORT_PATH, 'w') as export_file:
            export_file.write(str(gpio_number))

def unexport_gpio(gpio_number):
    with open(GPIO_UNEXPORT_PATH, 'w') as unexport_file:
        unexport_file.write(str(gpio_number))

def set_gpio_direction(gpio_number, direction):
    gpio_direction_path = GPIO_DIRECTION_PATH_TEMPLATE.format(gpio_number)
    with open(gpio_direction_path, 'w') as direction_file:
        direction_file.write(direction)

def set_gpio_value(gpio_number, value):
    gpio_value_path = GPIO_VALUE_PATH_TEMPLATE.format(gpio_number)
    with open(gpio_value_path, 'w') as value_file:
        value_file.write(str(value))

# Tone 재생 함수
def play_tone(gpio_number, frequency, duration):
    if frequency <= 0:
        print("Invalid frequency: Skipping tone")
        return
    
    period = 1.0 / frequency
    half_period = period / 2
    end_time = time.time() + duration

    while time.time() < end_time:
        set_gpio_value(gpio_number, 1)
        time.sleep(half_period)
        set_gpio_value(gpio_number, 0)
        time.sleep(half_period)

# IPC 데이터 처리 함수
def ipc_listener(gpio_pin):
    while True:
        if received_pucData:
            note = received_pucData[0]  # 첫 번째 바이트로 음계 결정
            duration = 0.5  # 기본 재생 시간
            
            if note in FREQUENCIES:
                print(f"Playing tone for note {note} at frequency {FREQUENCIES[note]} Hz")
                play_tone(gpio_pin, FREQUENCIES[note], duration)
            else:
                print(f"Received unknown note: {note}")
            time.sleep(0.1)  # IPC 데이터 처리 후 잠시 대기

# IPC 수신 스레드
def IPC_ReceivePacketFromIPCHeader(file_path):
    global received_pucData
    while True:
        # 여기서 실제 데이터 수신 구현을 해야 합니다.
        # 임의 데이터 예시 (테스트용)
        received_pucData = [1]  # C 노트 (261.63 Hz) 테스트용
        time.sleep(1)  # 임의로 1초마다 데이터 수신

# 메인 실행부
if __name__ == "__main__":
    gpio_pin = 89  # GPIO 핀 번호 설정

    try:
        export_gpio(gpio_pin)
        set_gpio_direction(gpio_pin, "out")

        # IPC 수신 스레드 실행
        ipc_thread = threading.Thread(target=IPC_ReceivePacketFromIPCHeader, args=("/dev/tcc_ipc_micom",))
        ipc_thread.daemon = True  # 프로그램 종료 시 스레드 종료
        ipc_thread.start()

        # GPIO를 사용해 음계 재생
        ipc_listener(gpio_pin)

    except KeyboardInterrupt:
        print("\nOperation stopped by User")
    finally:
        unexport_gpio(gpio_pin)

