import RPi.GPIO as GPIO
import time
import keyboard

# pin map
DR_BUTTON = 12
DR_SENSOR_LOCK = 26
DR_SENSOR_UNLOCK = 6
DR_SENSOR_DOOR = 19
DR_LED = 13

#door_status = 0

def switchPressed(channel):
    if channel == DR_SENSOR_LOCK:
        print('Door Locked')

    elif channel == DR_SENSOR_UNLOCK:
        print('Door Unlocked')

    elif channel == DR_SENSOR_DOOR:
        #if GPIO.input(DR_SENSOR_DOOR) != door_status :
        #    door_status = GPIO.input(DR_SENSOR_DOOR)
        if GPIO.input(DR_SENSOR_DOOR) == 0:
            print("Door Closed")
        else :
            print("Door Opened")


def initialize():
    GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)

    GPIO.setup([DR_BUTTON], GPIO.OUT, initial=GPIO.LOW) #, 16, 20, 21
    GPIO.setup([DR_SENSOR_LOCK, DR_SENSOR_UNLOCK, DR_SENSOR_DOOR, DR_LED], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(DR_SENSOR_LOCK, GPIO.RISING, callback=switchPressed)
    GPIO.add_event_detect(DR_SENSOR_UNLOCK, GPIO.RISING, callback=switchPressed)
    GPIO.add_event_detect(DR_SENSOR_DOOR, GPIO.BOTH, callback=switchPressed)


def main():
    initialize()

    #door_status = GPIO.input(DR_SENSOR_DOOR)

    print("Press ENTER to unlock...")
    print("Press Ctrl+C to exit...")

    try:
        while True:
            #GPIO.output(12, GPIO.HIGH)
            #time.sleep(0.1)
            #GPIO.output(12, GPIO.LOW)
            #time.sleep(30)

            if keyboard.is_pressed('enter') :
                GPIO.output(DR_BUTTON, GPIO.HIGH)
                print("Unlock/Lock door!!!")
                time.sleep(0.1)
                GPIO.output(DR_BUTTON, GPIO.LOW)
    except:
        pass

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
