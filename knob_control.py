import time
import board
import digitalio
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Define the pins for the encoder and button
CLK_PIN = board.GP2
DT_PIN = board.GP3
SW_PIN = board.GP5

# Initialize the encoder
encoder = rotaryio.IncrementalEncoder(CLK_PIN, DT_PIN)

# Initialize the button
button = digitalio.DigitalInOut(SW_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Initialize the consumer control for volume
cc = ConsumerControl(usb_hid.devices)

# Initialize the keyboard
keyboard = Keyboard(usb_hid.devices)

# Define keycodes for desktop switching and application switching
DESKTOP_NEXT = [Keycode.CONTROL, Keycode.WINDOWS, Keycode.RIGHT_ARROW]
DESKTOP_PREV = [Keycode.CONTROL, Keycode.WINDOWS, Keycode.LEFT_ARROW]
APP_SWITCH_WINDOWS_TAB = [Keycode.WINDOWS, Keycode.TAB]  # Windows + Tab

# Define application switching sequence (you can add more if needed)
APP_SWITCH_SEQUENCE = [APP_SWITCH_WINDOWS_TAB]
current_app_switch = 0

# Initialize mode and last encoder value
mode = 0  # 0: Volume control, 1: Desktop switching, 2: Application switching
last_encoder_value = encoder.position

# Main loop
while True:
    # Read the encoder value
    encoder_value = encoder.position
    
    # Calculate the change in encoder value
    delta = encoder_value - last_encoder_value
    
    # Check for button press to change mode
    if not button.value:
        mode = (mode + 1) % 3
        time.sleep(0.2)  # Debounce
        
        if mode == 0:
            print("Mode: Volume Control")
        elif mode == 1:
            print("Mode: Desktop Switching")
        else:
            print("Mode: Application Switching")
    
    # Check encoder rotation based on mode
    if encoder_value > last_encoder_value:
        if mode == 0:
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        elif mode == 1:
            keyboard.send(*DESKTOP_NEXT)  # Switch to the next desktop
        elif mode == 2:
            keyboard.send(*APP_SWITCH_SEQUENCE[current_app_switch])  # Switch applications
            current_app_switch = (current_app_switch + 1) % len(APP_SWITCH_SEQUENCE)
    elif encoder_value < last_encoder_value:
        if mode == 0:
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        elif mode == 1:
            keyboard.send(*DESKTOP_PREV)  # Switch to the previous desktop
    
    # Update last encoder value
    last_encoder_value = encoder_value
    
    # Add a delay to prevent excessive loop iterations
    time.sleep(0.05)
