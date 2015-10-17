import RPi.GPIO as GPIO
import time


MATRIX = [['1', '2', '3'],
          ['4', '5', '6'],
          ['7', '8', '9'],
          ['*', '0', '#']]
ROW = [18, 23, 24, 25]
COL = [4, 17, 22]


# !IMPORTANT! requires sudo privileges to read from GPIO ports!
class MatrixKey:

    def __init__(self):
        self.gpio_setup()
        self.t0 = time.time()
        self.is_key_down = False
        self.check = -1

    def gpio_setup(self):
        GPIO.setmode(GPIO.BCM)
        for j in range(3):
            GPIO.setup(COL[j], GPIO.OUT)
            GPIO.output(COL[j], 1)
        for i in range(4):
            GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_input(self):
        try:
            if time.time() - self.t0 > 0.3:  # debounce
                if self.is_key_down:
                    if GPIO.input(ROW[self.check]) != 0:
                        self.check = -1
                        self.is_key_down = False
                else:
                    for j in range(3):
                        GPIO.output(COL[j], 0)
                        for i in range(4):
                            if GPIO.input(ROW[i]) == 0:
                                self.check = i
                                self.is_key_down = True
                                self.t0 = time.time()
                                return MATRIX[i][j]
                        GPIO.output(COL[j], 1)
        except KeyboardInterrupt:
            GPIO.cleanup()


# m = MatrixKey()
# while True:
#     input = m.read_input()
#     if input != None:
#         print input
