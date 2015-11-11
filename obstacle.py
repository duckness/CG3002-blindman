from audio import Audio
import operator
import math


# the minimum distance in cm needed to an object before the beep will start triggering
MIN_DISTANCE_us = 50
MIN_DISTANCE_ir = 50
SENSOR_TOWARDS_GROUND = 1
STEP_HEIGHT = 20

PERCENTAGE_OBSTACLE = 0.6
PERCENTAGE_MIN = 0.8
PERCENTAGE_MAX = 1.2
BUFFER_MIN = 0.95
BUFFER_MAX = 1.05

#obstacles left:0, front(u/s): 1, front(i/r): 2,right: 3

"""
Assumption for incoming array
Front
Right
Left
Back
CALIBRATION - max and min
sensor - 85% of min, 115% of max
"""

class ObstacleCues:
    FRONT_OBSTACLES = 1
    RIGHT_OBSTACLES = 2
    LEFT_OBSTACLES = 3
    OBSTACLE_STEP_UP = 4
    OBSTACLE_STEP_DOWN= 5
    NO_OBSTACLES = 0

    LEFT_PATH_FREE = 1
    RIGHT_PATH_FREE = 2
    BOTH_SIDE_FREE = 3
    NO_ALT_ROUTE = 0
    # todo: map all the sensors to the location it corresponds
    # fixme: IMO, I think it is simpler to just send the lesser value of the two sensors pointing in the same direction
    index_to_direction = {0: "beep_left",
                          1: "beep_mid",
                          2: "beep_mid",
                          3: "beep_right"
                          }

    def __init__(self):
        self.audio = Audio()
        self.avg_height_below = 50
        self.calibrate = []
        self.max_height_breathe = 0
        self.min_height_breathe = 999
        self.raw_avg = 0
        self.diff = 0


    def get_checksum(self, strn):
        checksum = 0
        for i in xrange(0, len(strn)):
            checksum = operator.xor(checksum, ord(strn[i]))
        return checksum

    # todo: actually scan serial instead of a file
    """
    def scan_serial(self):
        f = open('demo.txt')
        for line in f:
            if line[0] == '1':  # only care about the ultrasonic sensors
                sensors = map(int, line.split(", "))
                distance = [] # dummy array
                # todo: add checksum as well
                if sensors[1] == 0:  # 0 means out of range
                    continue
                else:
                    if distance[0][1] <= MIN_DISTANCE_us or distance[0][2] <= MIN_DISTANCE_ir :
                        alert_direction = self.index_to_direction[int(line[1])]
                        self.audio.play_sound(self.audio.sounds[alert_direction])
                        self.alt_route(distance)
                    for i in range(1,3):
                        if distance[i][1] <= MIN_DISTANCE_us or distance[i][2] <= MIN_DISTANCE_ir :
                            alert_direction = self.index_to_direction[int(line[1])]
                            self.audio.play_sound(self.audio.sounds[alert_direction])

                """
    #def calibrate_height_below(self,array):
    #    return sum(array)/len

    #def calibrate_max(self, value):
        #self.max_height_breathe = array[0]
        #self.min_height_breathe = array[0]
        #for values in array:
        #self.calibrate.append(cali_arr[1])
        #self.avg_height_below = (self.max_height_breathe + self.min_height_breathe)/2
        #print self.avg_height_below
        #self.calibrate_max(self.calibrate)
        #self.diff = self.max_height_breathe - self.min_height_breathe
        #print self.diff
        #cali_arr is [us, ir] of the sensor to calibrate
        # if cali_arr[1] > self.max_height_breathe:
        #     self.max_height_breathe = cali_arr[1] * BUFFER_MAX
        # if cali_arr[1] < self.min_height_breathe:
        #     self.min_height_breathe = cali_arr[1] * BUFFER_MIN


    def initial_calibration(self,cali_arr):
        if cali_arr[1] >= 30 and cali_arr[1] <= 150:
            self.calibrate.append(cali_arr[1])
        if len(self.calibrate) == 0:
            return
        self.calibrate.sort()
        self.max_height_breathe = sum(self.calibrate)/len(self.calibrate)
        self.min_height_breathe = sum(self.calibrate)/len(self.calibrate)
        print self.max_height_breathe, self.min_height_breathe

    def detect_obstacles(self,obstacles):
        for i,value in enumerate(obstacles):
            #print i, value
            if i != SENSOR_TOWARDS_GROUND:
                if (value[0] <= MIN_DISTANCE_us and value[0] > 0) or (value[1] <= MIN_DISTANCE_ir and value[1] > 0):
                    alert_direction = self.index_to_direction[i]
                    #print "obstacle at " + str(alert_direction)
                    #print i, value[0], value[1]
                    # print alert_direction
                    if i == 1 or i == 2:
                        return self.FRONT_OBSTACLES
                    else:
                        self.audio.play_beep(alert_direction)

            else:
                # if value[1] < (self.min_height_breathe * PERCENTAGE_MIN):  #i/r sensor
                if self.min_height_breathe - value[1] > STEP_HEIGHT and self.min_height_breathe - value[1] < STEP_HEIGHT*2:
                    alert_direction = self.index_to_direction[i]
                    #print "obstacle at " + str(alert_direction)
                    #print 1, value[1], self.min_height_breathe
                    return self.OBSTACLE_STEP_UP
                # elif value[1] > (self.max_height_breathe * PERCENTAGE_MAX):
                elif value[1] - self.max_height_breathe > STEP_HEIGHT and value[1] - self.max_height_breathe < STEP_HEIGHT*2:
                    #print 1, value[1], self.max_height_breathe
                    return self.OBSTACLE_STEP_DOWN
                if (value[0] <= MIN_DISTANCE_us and value[0] > 0):
                    #print "us"
                    #print 1, value[0]
                    alert_direction = self.index_to_direction[i]
                    #print "obstacle at " + str(alert_direction)
                    #self.audio.play_beep(alert_direction)
                    return self.FRONT_OBSTACLES
        return self.NO_OBSTACLES

    def alt_route(self,distance):
        obstaclesfound=[1,0,0,0]; #front,left,right,no alt route
        if not self.detect_ostacle_right(distance[3]):
            obstaclesfound[2] = 1
            obstaclesfound[3] += 1
        if not self.detect_ostacle_left(distance[0]):
            obstaclesfound[1] = 1
            obstaclesfound[3] += 1
        #if not self.detect_ostacle_behind(distance[3]):
            #return True
        if obstaclesfound[3] == 2:
            return self.BOTH_SIDE_FREE
        elif obstaclesfound[1] == 1:
            return self.LEFT_PATH_FREE
        elif obstaclesfound[2] == 1:
            return self.RIGHT_PATH_FREE
        #self.audio.play_sound('around') # THIS IS ONLY CALLED WHEN THERE ARE OBSTACLES RIGHT, LEFT ,FRONT
        return self.NO_ALT_ROUTE


    def detect_ostacle_right(self,distance):
        if (distance[0] <= MIN_DISTANCE_us and distance[0] > 0) or (distance[1] <= MIN_DISTANCE_ir and distance[1] > 0): # should base on navigation between left and righT
            return True
        return False

    def detect_ostacle_left(self,distance):
        if (distance[0] <= MIN_DISTANCE_us and distance[0] > 0) or (distance[1] <= MIN_DISTANCE_ir and distance[1] > 0): # should base on navigation between left and right
            return True
        return False

    """

    def detect_ostacle_behind(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            print "turn around"
            self.audio.play_sound('around')
            self.audio.play_sound('go')
        else:
            return True
        return False
    """

#obs = ObstacleCues()
#sensors = [[0,0],[0,0],[0,0],[0,0]]
#while(1):
#    sensors[0][0] =  int(raw_input("Enter sensor 1 "))
#    sensors[0][1] =  int(raw_input("Enter sensor 1 "))
#    sensors[1][0] =  int(raw_input("Enter sensor 2 "))
#    sensors[1][1] =  int(raw_input("Enter sensor 2 "))
#    sensors[2][0] =  int(raw_input("Enter sensor 3 "))
#    sensors[2][1] =  int(raw_input("Enter sensor 3 "))
#    sensors[3][0] =  int(raw_input("Enter sensor 4 "))
#    sensors[3][1] =  int(raw_input("Enter sensor 4 "))
#    obs.detect_obstacles(sensors)
