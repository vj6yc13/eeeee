import sys
import os
import time

# GPIO 관련 경로 및 설정
GPIO_EXPORT_PATH = "/sys/class/gpio/export"
GPIO_UNEXPORT_PATH = "/sys/class/gpio/unexport"
GPIO_DIRECTION_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/direction"
GPIO_VALUE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/value"
GPIO_BASE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}"

# 음계 주파수 (Hz)
FREQUENCIES = {
    'C': 261.63,  # 도
    'D': 293.66,  # 레
    'E': 329.63,  # 미
    'F': 349.23,  # 파
    'G': 392.00,  # 솔
    'A': 440.00,  # 라
    'B': 493.88,  # 시
    'C5': 523.25  # 높은 도
}

# 나비야 멜로디 (음과 길이)
# (음 이름, 길이(초))
MELODY = [
    ('C', 0.5), ('D', 0.5), ('E', 0.5), ('C', 0.5),
    ('E', 0.5), ('F', 0.5), ('G', 1.0),
    ('E', 0.5), ('F', 0.5), ('E', 0.5), ('D', 0.5), ('C', 1.0),
]

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

def play_tone(gpio_number, frequency, duration):
    period = 1.0 / frequency
    half_period = period / 2
    end_time = time.time() + duration

    while time.time() < end_time:
        set_gpio_value(gpio_number, 1)
        time.sleep(half_period)
        set_gpio_value(gpio_number, 0)
        time.sleep(half_period)

if __name__ == "__main__":
    gpio_pin = 89  # 제공된 핀 번호 유지

    try:
        export_gpio(gpio_pin)
        set_gpio_direction(gpio_pin, "out")

        for note, length in MELODY:
            if note in FREQUENCIES:
                print(f"Playing {note} at {FREQUENCIES[note]} Hz")
                play_tone(gpio_pin, FREQUENCIES[note], length)
            time.sleep(0.1)  # 음 사이의 간격
    except KeyboardInterrupt:
        print("\nOperation stopped by User")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        unexport_gpio(gpio_pin)

    sys.exit(0)

