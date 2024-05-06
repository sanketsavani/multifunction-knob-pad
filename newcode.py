import time
import board
import digitalio
import rotaryio
import analogio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Define the pins for the encoder and buttons
CLK_PIN = board.GP0
DT_PIN = board.GP1
SW_PIN = board.GP2
DESKTOP_PREV_PIN = board.GP4
DESKTOP_NEXT_PIN = board.GP5
MEDIA_CONTROL_PIN = board.GP12
MICROPHONE_MUTE_PIN = board.GP10  # Added for microphone mute

# Define the pins for the joystick
JOYSTICK_SW_PIN = board.GP26
JOYSTICK_VRY_PIN = board.GP27
JOYSTICK_VRX_PIN = board.GP28

# Initialize the encoder
encoder = rotaryio.IncrementalEncoder(CLK_PIN, DT_PIN)

# Initialize the button
button = digitalio.DigitalInOut(SW_PIN)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Initialize the desktop switches
desktop_prev_switch = digitalio.DigitalInOut(DESKTOP_PREV_PIN)
desktop_next_switch = digitalio.DigitalInOut(DESKTOP_NEXT_PIN)
desktop_prev_switch.direction = digitalio.Direction.INPUT
desktop_next_switch.direction = digitalio.Direction.INPUT
desktop_prev_switch.pull = digitalio.Pull.UP
desktop_next_switch.pull = digitalio.Pull.UP

# Initialize the media control button
media_control_switch = digitalio.DigitalInOut(MEDIA_CONTROL_PIN)
media_control_switch.direction = digitalio.Direction.INPUT
media_control_switch.pull = digitalio.Pull.UP

# Initialize the microphone mute button
microphone_mute_switch = digitalio.DigitalInOut(MICROPHONE_MUTE_PIN)
microphone_mute_switch.direction = digitalio.Direction.INPUT
microphone_mute_switch.pull = digitalio.Pull.UP

# Initialize the joystick button
joystick_button = digitalio.DigitalInOut(JOYSTICK_SW_PIN)
joystick_button.direction = digitalio.Direction.INPUT
joystick_button.pull = digitalio.Pull.UP

# Initialize the joystick analog input pins
joystick_vry = analogio.AnalogIn(JOYSTICK_VRY_PIN)
joystick_vrx = analogio.AnalogIn(JOYSTICK_VRX_PIN)

# Initialize the consumer control for volume
cc = ConsumerControl(usb_hid.devices)

# Initialize the keyboard
keyboard = Keyboard(usb_hid.devices)

# Define keycodes for desktop switching
DESKTOP_NEXT = [Keycode.CONTROL, Keycode.WINDOWS, Keycode.RIGHT_ARROW]  # Windows/Linux: Ctrl + Win + Right
DESKTOP_PREV = [Keycode.CONTROL, Keycode.WINDOWS, Keycode.LEFT_ARROW]   # Windows/Linux: Ctrl + Win + Left

# Define keycodes for application switching (add as many as needed)
APP_SWITCH_SEQUENCE = [
    [Keycode.ALT, Keycode.TAB],       # Alt + Tab for application switching
    [Keycode.ALT, Keycode.TAB, Keycode.SHIFT],  # Alt + Shift + Tab for reverse switching
    # Add more application key sequences here
]

# Define the media control keycode
MEDIA_PLAY_PAUSE = ConsumerControlCode.PLAY_PAUSE

# Define the microphone mute/unmute keycode
MICROPHONE_MUTE = ConsumerControlCode.MUTE

# Initialize mode and last encoder value
mode = 0  # 0: Volume control, 1: Application switching
last_encoder_value = encoder.position

# Initialize the current app switch index
current_app_switch = 0

# Initialize button state variables
prev_desktop_prev_state = True
prev_desktop_next_state = True
prev_media_control_state = True
prev_microphone_mute_state = True

# Initialize joystick position variables
last_joystick_vry_value = 32768
last_joystick_vrx_value = 32768

# Define joystick threshold
JOYSTICK_THRESHOLD = 5000  # Adjust as needed

# Main loop
while True:
    # Read the encoder value
    encoder_value = encoder.position
    
    # Calculate the change in encoder value
    delta = encoder_value - last_encoder_value
    
    # Check for button press to change mode
    if not button.value:
        mode = (mode + 1) % 2
        time.sleep(0.2)  # Debounce
        
        if mode == 0:
            print("Mode: Volume Control")
        else:
            print("Mode: Application Switching")
    
    # Check encoder rotation based on mode
    if encoder_value > last_encoder_value:
        if mode == 0:
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        elif mode == 1:
            # Switch to the next application in the sequence
            keyboard.send(*APP_SWITCH_SEQUENCE[current_app_switch])
            current_app_switch = (current_app_switch + 1) % len(APP_SWITCH_SEQUENCE)
    elif encoder_value < last_encoder_value:
        if mode == 0:
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        elif mode == 1:
            # Switch to the previous application in the sequence
            current_app_switch = (current_app_switch - 1) % len(APP_SWITCH_SEQUENCE)
            keyboard.send(*APP_SWITCH_SEQUENCE[current_app_switch])
    
    # Check for desktop switch button press
    desktop_prev_state = not desktop_prev_switch.value
    desktop_next_state = not desktop_next_switch.value
    
    if desktop_prev_state and not prev_desktop_prev_state:
        print("Desktop Previous Switch")
        keyboard.send(*DESKTOP_PREV)  # Switch desktops
    
    if desktop_next_state and not prev_desktop_next_state:
        print("Desktop Next Switch")
        keyboard.send(*DESKTOP_NEXT)  # Switch desktops
    
    prev_desktop_prev_state = desktop_prev_state
    prev_desktop_next_state = desktop_next_state
    
    # Check for media control button press
    media_control_state = not media_control_switch.value
    
    if media_control_state and not prev_media_control_state:
        print("Media Control Switch")
        cc.send(MEDIA_PLAY_PAUSE)  # Play/Pause
    
    prev_media_control_state = media_control_state
    
    # Check for microphone mute button press
    microphone_mute_state = not microphone_mute_switch.value
    
    if microphone_mute_state and not prev_microphone_mute_state:
        print("Microphone Mute Switch")
        cc.send(MICROPHONE_MUTE)  # Mute/Unmute
    
    prev_microphone_mute_state = microphone_mute_state
    
    # Read joystick position
    joystick_vry_value = joystick_vry.value
    print("joystick_vry_value",joystick_vry_value)
    joystick_vrx_value = joystick_vrx.value
    print("joystick_vrx_value",joystick_vrx_value)
    
    # Check if joystick has moved vertically
    if abs(joystick_vry_value - last_joystick_vry_value) > JOYSTICK_THRESHOLD:
        if joystick_vry_value < last_joystick_vry_value:
            # Joystick moved up
            # Perform scrolling up action
            print("Joystick moved up")
            # Implement scrolling up action here
        else:
            # Joystick moved down
            # Perform scrolling down action
            print("Joystick moved down")
            # Implement scrolling down action here
    
    # Check if joystick has moved horizontally
    if abs(joystick_vrx_value - last_joystick_vrx_value) > JOYSTICK_THRESHOLD:
        if joystick_vrx_value < last_joystick_vrx_value:
            # Joystick moved left
            # Perform scrolling left action
            print("Joystick moved left")
            # Implement scrolling left action here
        else:
            # Joystick moved right
            # Perform scrolling right action
            print("Joystick moved right")
            # Implement scrolling right action here
    
    # Update last encoder value
    last_encoder_value = encoder_value
    
    # Update last joystick values
    last_joystick_vry_value = joystick_vry_value
    last_joystick_vrx_value = joystick_vrx_value
    
    # Add a delay to prevent excessive loop iterations
    time.sleep(0.05)
