import os
import time
import threading

# GPIO 경로 및 설정
GPIO_BASE_PATH = "/sys/class/gpio"
GPIO_EXPORT_PATH = os.path.join(GPIO_BASE_PATH, "export")
GPIO_UNEXPORT_PATH = os.path.join(GPIO_BASE_PATH, "unexport")

# GPIO 핀 제어 함수
def gpio_export(pin):
    if not os.path.exists(os.path.join(GPIO_BASE_PATH, f"gpio{pin}")):
        with open(GPIO_EXPORT_PATH, 'w') as f:
            f.write(str(pin))

def gpio_unexport(pin):
    with open(GPIO_UNEXPORT_PATH, 'w') as f:
        f.write(str(pin))

def gpio_set_direction(pin, direction):
    direction_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "direction")
    with open(direction_path, 'w') as f:
        f.write(direction)

def gpio_write(pin, value):
    value_path = os.path.join(GPIO_BASE_PATH, f"gpio{pin}", "value")
    with open(value_path, 'w') as f:
        f.write(str(value))

# LCD 핀 설정
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

# LCD 초기화 함수
def lcd_init():
    for pin in [LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
        gpio_export(pin)
        gpio_set_direction(pin, "out")
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    gpio_write(LCD_RS, mode)
    for i, pin in enumerate([LCD_D4, LCD_D5, LCD_D6, LCD_D7]):
        gpio_write(pin, "1" if bits & (1 << (4 + i)) else "0")
    lcd_toggle_enable()
    for i, pin in enumerate([LCD_D4, LCD_D5, LCD_D6, LCD_D7]):
        gpio_write(pin, "1" if bits & (1 << i) else "0")
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

# 부저 핀 설정 및 음계
BUZZER_PIN = 89
FREQUENCIES = {
    'C': 261.63, 'D': 293.66, 'E': 329.63,
    'F': 349.23, 'G': 392.00, 'A': 440.00, 'B': 493.88, 'C5': 523.25, 'D5' : 587.33, 'E5' : 659.26
}
MELODY = [
    ('D', 0.5), ('B', 0.5), ('A', 0.5), ('G', 0.5), ('D', 1.0),
    ('D', 0.5), ('B', 0.5), ('A', 0.5), ('G', 0.5), ('E', 1.0),
    ('E', 0.5), ('C5', 0.5), ('B', 0.5), ('A', 0.5), ('F', 1.0),
    ('D5', 0.5), ('D5', 0.5), ('C5', 0.5), ('A', 0.5), ('B', 1.0), ('G', 1.0),
    ('D', 0.5), ('B', 0.5), ('A', 0.5), ('G', 0.5), ('D', 1.0),
    ('D', 0.5), ('B', 0.5), ('A', 0.5), ('G',0.5), ('E', 1.0),
    ('E', 0.5), ('C5', 0.5), ('B', 0.5), ('A', 0.5), ('D5', 1.5), ('D5', 1.5), ('D5', 0.5), ('D5', 0.5),
    ('E5', 0.5), ('D5', 0.5), ('C5', 0.5), ('A', 0.5), ('G', 1.0), ('B', 1.0),
    ('B', 0.5), ('B', 0.5), ('B', 1.0), ('B', 0.5), ('B', 0.5), ('B', 1.0), ('B', 0.5), ('D5', 0.5), ('G', 0.5), ('A', 0.5), ('B', 1.5),
    ('C5', 0.5), ('C5', 0.5), ('C5', 1.5), ('C5', 0.5), ('C5', 0.5), ('B', 0.5), ('B', 0.5), ('B', 0.5), ('B', 0.5), ('A', 0.5), ('A', 0.5), ('G', 0.5), ('A', 1.0), ('B', 1.0),
    ('B', 0.5), ('B', 0.5), ('B', 1.0), ('B', 0.5), ('B', 0.5), ('B', 1.0), ('B', 0.5), ('D5', 0.5), ('G', 0.5), ('A', 0.5), ('B', 1.5),
    ('C5', 0.5), ('C5', 0.5), ('C5', 1.5), ('C5', 0.5), ('C5', 0.5), ('B', 0.5), ('B', 0.5), ('B', 0.5), ('D5', 0.5), ('D5', 0.5), ('C5', 0.5), ('A', 0.5), ('G', 2.0)
    
]

def play_tone(pin, frequency, duration):
    period = 1.0 / frequency
    half_period = period / 2
    end_time = time.time() + duration
    while time.time() < end_time:
        gpio_write(pin, 1)
        time.sleep(half_period)
        gpio_write(pin, 0)
        time.sleep(half_period)

# 멜로디 재생
def play_melody():
    gpio_export(BUZZER_PIN)
    gpio_set_direction(BUZZER_PIN, "out")
    try:
        for note, length in MELODY:
            if note in FREQUENCIES:
                play_tone(BUZZER_PIN, FREQUENCIES[note], length)
            time.sleep(0.1)
    finally:
        gpio_unexport(BUZZER_PIN)

# LCD 메시지 표시
def display_lcd():
    lcd_init()
    try:
        while True:
            lcd_string("Let's play!", LCD_LINE_1)
            lcd_string("**Jingle Bell**", LCD_LINE_2)
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nLCD stopped.")
    finally:
        for pin in [LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
            gpio_unexport(pin)

# 메인 실행
if __name__ == "__main__":
    try:
        # 멀티스레드 실행
        lcd_thread = threading.Thread(target=display_lcd)
        buzzer_thread = threading.Thread(target=play_melody)

        lcd_thread.start()
        buzzer_thread.start()

        lcd_thread.join()
        buzzer_thread.join()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")