﻿from audio import Audio
import operator
import math


# the minimum distance in cm needed to an object before the beep will start triggering
MIN_DISTANCE_us = 20
MIN_DISTANCE_ir = 20
SENSOR_TOWARDS_GROUND = 2
AVG_HEIGHT_STAIRS = 15.0
FRONT_OBSTACLES = 1
RIGHT_OBSTACLES = 2
LEFT_OBSTACLES = 3
OBSTACLE_LOWER = 4
OBSTACLE_STEP_DOWN= 5
NO_OBSTACLES = 0

LEFT_PATH_FREE = 1
RIGHT_PATH_FREE = 2
BOTH_SIDE_FREE = 3
NO_ALT_ROUTE = 0

#obstacles left:0, front(u/s): 1, front(i/r): 2,right: 3

"""
Assumption for incoming array
Front
Right
Left
Back
"""

class ObstacleCues:

    # todo: map all the sensors to the location it corresponds
    # fixme: IMO, I think it is simpler to just send the lesser value of the two sensors pointing in the same direction
    index_to_direction = {0: "beep_left",
                          1: "beep_mid",
                          2: "beep_mid",
                          3: "beep_right"
                          }

    def __init__(self):
        self.audio = Audio()
        self.avg_height_below = 0
        self.calibrate = []

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
    def calibrate_height_below(self,array):
        return sum(array)/len(array)

    def initial_calibration(self,cali_arr):
        self.calibrate.append(cali_arr[1])
        self.avg_height_below = self.calibrate_height_below(self.calibrate)


    def detect_obstacles(self,obstacles):
        for i,value in enumerate(obstacles):
            #print i, value
            if value[0] != 0 or value[1]!= 0:
                if i != SENSOR_TOWARDS_GROUND:
                    if value[0] <= MIN_DISTANCE_us or value[1] <= MIN_DISTANCE_ir :
                        alert_direction = self.index_to_direction[i]
                        #print "obstacle at " + str(alert_direction)
                        #self.audio.play_sound(self.audio.sounds[alert_direction])
                        self.audio.play_sound(alert_direction)
                        if i == 1 or i == 2:
                            return FRONT_OBSTACLES
                        """
                        if i == 0:
                            return LEFT_OBSTACLES
                        if i == 3:
                            return RIGHT_OBSTACLES
                        """
                else:
                    if value[1] <= self.avg_height_below :  #i/r sensor
                        alert_direction = self.index_to_direction[i]
                        #print "obstacle at " + str(alert_direction)
                        #self.audio.play_sound(self.audio.sounds[alert_direction])
                        self.audio.play_sound(alert_direction)
                        self.audio.play_sound('near_knee')
                        return OBSTACLE_LOWER
                    elif value[1] >= (self.avg_height_below + AVG_HEIGHT_STAIRS):
                        self.audio.play_sound('step_below')
                        return OBSTACLE_STEP_DOWN
                    if value[0] <= MIN_DISTANCE_us:
                        alert_direction = self.index_to_direction[i]
                        #print "obstacle at " + str(alert_direction)
                        #self.audio.play_sound(self.audio.sounds[alert_direction])
                        self.audio.play_sound(alert_direction)
                        return FRONT_OBSTACLES
        return NO_OBSTACLES




    def alt_route(self,distance):   #
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
            return BOTH_SIDE_FREE
        elif obstaclesfound[1] == 1:
            return LEFT_PATH_FREE
        elif obstaclesfound[2] == 1:
            return RIGHT_PATH_FREE
        self.audio.play_sound('around') # THIS IS ONLY CALLED WHEN THERE ARE OBSTACLES RIGHT, LEFT ,FRONT
        return NO_ALT_ROUTE


    def detect_ostacle_right(self,distance):
        if distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir: # should base on navigation between left and righT
            return True
        return False

    def detect_ostacle_left(self,distance):
        if distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir: # should base on navigation between left and right
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