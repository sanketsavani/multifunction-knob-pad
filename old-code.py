import digitalio
import board
import usb_hid
import time
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

print("== Pi Pico multifunction knob 1.0 ==")

CLK_PIN = board.GP4
DT_PIN = board.GP3
SW_PIN = board.GP2
clk_last = None
count = 0
totalMode = 3
currentMode = 0

cc = ConsumerControl(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)


clk = digitalio.DigitalInOut(CLK_PIN)
clk.direction = digitalio.Direction.INPUT

dt = digitalio.DigitalInOut(DT_PIN)
dt.direction = digitalio.Direction.INPUT

sw = digitalio.DigitalInOut(SW_PIN)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP

def millis():
    return time.monotonic() * 1000

def ccw():
    print("CCW")
    
    if (currentMode == 0):    # Mac brightness down
        keyboard.send(Keycode.SCROLL_LOCK)
        
    elif(currentMode ==1):    # Mac horizontal scroll right
        keyboard.press(Keycode.SHIFT)
        mouse.move(wheel=-1)
        keyboard.release(Keycode.SHIFT)

    elif(currentMode == 2):   # Volume decrement
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        
def cw():
    print("CW")
    if (currentMode == 0):     # Mac brightness up
        keyboard.send(Keycode.PAUSE)              
        
    elif(currentMode ==1):     # Mac horizontal scroll left
        keyboard.press(Keycode.SHIFT)
        mouse.move(wheel=1)
        keyboard.release(Keycode.SHIFT)
   
    elif(currentMode == 2):     # Volume increment
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)

        
def long_press():
    #Mac sleep: CMD + OPT + EJECT
    keyboard.press(Keycode.ALT, Keycode.COMMAND)  
    cc.send(ConsumerControlCode.EJECT)
    keyboard.release_all()

while(1):
    clkState = clk.value
    if(clk_last !=  clkState):
        if(dt.value != clkState):
            cw()
        else:
            ccw()
            
    if (sw.value == 0):
        pressTime = millis()
        time.sleep(0.2)
        longPress = False
        
        while(sw.value == 0):
            if(millis() - pressTime > 1000 and not longPress):
                print("longPress")
                longPress = True
                long_press()
                

        if (not longPress):
            currentMode += 1
            currentMode %= totalMode
            print("Mode: " + str(currentMode))
            
    clk_last = clkState
    