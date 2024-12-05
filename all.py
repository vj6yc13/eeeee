import RPi.GPIO as GPIO
import time
import os
import time
import sys

# GPIO path
GPIO_BASE_PATH = "/sys/class/gpio"
GPIO_EXPORT_PATH = os.path.join(GPIO_BASE_PATH, "export")
GPIO_UNEXPORT_PATH = os.path.join(GPIO_BASE_PATH, "unexport")
GPIO_DIRECTION_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/direction"
GPIO_VALUE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}/value"
GPIO_BASE_PATH_TEMPLATE = "/sys/class/gpio/gpio{}"

# LCD pin definitions
LCD_RS = 117  
LCD_E  = 121  
LCD_D4 = 114  
LCD_D5 = 113  
LCD_D6 = 112  
LCD_D7 = 61  

LCD_WIDTH = 16
LCD_CHR = "1"
LCD_CMD = "0"

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

E_PULSE = 0.0005
E_DELAY = 0.0005

# Tone frequencies (Hz)
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

# Melody for "나비야"
MELODY = [
    ('C', 0.5), ('D', 0.5), ('E', 0.5), ('C', 0.5),
    ('E', 0.5), ('F', 0.5), ('G', 1.0),
    ('E', 0.5), ('F', 0.5), ('E', 0.5), ('D', 0.5), ('C', 1.0),
]

# GPIO control functions
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

# Tone playing
def play_tone(gpio_number, frequency, duration):
    period = 1.0 / frequency
    half_period = period / 2
    end_time = time.time() + duration

    while time.time() < end_time:
        set_gpio_value(gpio_number, 1)
        time.sleep(half_period)
        set_gpio_value(gpio_number, 0)
        time.sleep(half_period)

# LCD control functions
def lcd_init():
    for pin in [LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
        export_gpio(pin)
        set_gpio_direction(pin, "out")

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    gpio_write(LCD_RS, mode)
    gpio_write(LCD_D4, "0")
    gpio_write(LCD_D5, "0")
    gpio_write(LCD_D6, "0")
    gpio_write(LCD_D7, "0")

    if bits & 0x10 == 0x10:
        gpio_write(LCD_D4, "1")
    if bits & 0x20 == 0x20:
        gpio_write(LCD_D5, "1")
    if bits & 0x40 == 0x40:
        gpio_write(LCD_D6, "1")
    if bits & 0x80 == 0x80:
        gpio_write(LCD_D7, "1")

    lcd_toggle_enable()

    gpio_write(LCD_D4, "0")
    gpio_write(LCD_D5, "0")
    gpio_write(LCD_D6, "0")
    gpio_write(LCD_D7, "0")

    if bits & 0x01 == 0x01:
        gpio_write(LCD_D4, "1")
    if bits & 0x02 == 0x02:
        gpio_write(LCD_D5, "1")
    if bits & 0x04 == 0x04:
        gpio_write(LCD_D6, "1")
    if bits & 0x08 == 0x08:
        gpio_write(LCD_D7, "1")

    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(E_DELAY)
    gpio_write(LCD_E, "1")
    time.sleep(E_PULSE)
    gpio_write(LCD_E, "0")
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# Main function
if __name__ == "__main__":
    gpio_pin = 89  # Buzzer GPIO pin

    try:
        # Initialize GPIO and LCD
        export_gpio(gpio_pin)
        set_gpio_direction(gpio_pin, "out")
        lcd_init()

        # Play melody and display notes on LCD
        for note, duration in MELODY:
            if note in FREQUENCIES:
                lcd_string(f"Playing: {note}", LCD_LINE_1)
                print(f"Playing {note} at {FREQUENCIES[note]} Hz")
                play_tone(gpio_pin, FREQUENCIES[note], duration)
            time.sleep(0.1)  # Pause between notes

        lcd_string("Melody Done", LCD_LINE_1)
        print("Melody finished.")
        time.sleep(2)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        # Cleanup GPIO
        unexport_gpio(gpio_pin)
        for pin in [LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
            unexport_gpio(pin)

