import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


class Button:
    def __init__(self, pin, bouncetime=200):
        self.pin = pin
        self.bouncetime = bouncetime

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)

    @property
    def pressed(self):
        return not GPIO.input(self.pin)

    def on_action(self, call_method):
        GPIO.add_event_detect(self.pin, GPIO.BOTH, call_method, bouncetime=self.bouncetime)
