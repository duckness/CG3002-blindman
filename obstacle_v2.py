from audio import Audio
from random import randint

# constant
MIN_DISTANCE    = 50
SENSOR_GROUND   = 1
STEP            = 20

class ObstacleCues:
    # constants
    FRONT_OBSTACLES     = 1
    RIGHT_OBSTACLES     = 2
    LEFT_OBSTACLES      = 3
    OBSTACLE_STEP_UP    = 4
    OBSTACLE_STEP_DOWN  = 5
    NO_OBSTACLES        = 0
    index_to_direction  = { 0: 'beep_left',
                            1: 'beep_mid',
                            2: 'beep_mid',
                            3: 'beep_right' }

    def __init__(self):
        self.audio = Audio()
        self.ground_height = 0
        self.calibrates = []
        self.return_val = []

    def initial_calibration(self, val):
        self.calibrates.append(val[1])
        self.ground_height = sum(self.calibrates) / len(self.calibrates)
        print self.ground_height

    def detect_obstacles(self, sensors):
        self.return_val = []
        # ultrasonics
        for i in range(0, 4):
            val = sensors[i][0]
            val2 = sensors[i][1]
            if (val > 0 and val <= MIN_DISTANCE) or (val2 > 20  and val2 <= MIN_DISTANCE):
                if (i == 1 or i == 2) and val2 <= MIN_DISTANCE*2:
                    self.return_val.append(self.FRONT_OBSTACLES)
                    print i, val, val2
                    # print 'front front front', i
                else:
                    self.audio.play_beep(self.index_to_direction[i])
                    # print val, val2, self.index_to_direction[i]

        # infrared
        for i in range(0, 4):
            val = sensors[i][1]
            if i == SENSOR_GROUND:
                if val > self.ground_height+STEP:
                    # step down
                    self.return_val.append(self.OBSTACLE_STEP_DOWN)
                elif val < self.ground_height-STEP:
                    # step up
                    self.return_val.append(self.OBSTACLE_STEP_UP)
                else:
                    pass

        if len(self.return_val) == 0:
            return self.NO_OBSTACLES
        else:
            self.return_val.sort()
            return self.return_val[0]
