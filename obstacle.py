from audio import Audio
import operator
import math


# the minimum distance in cm needed to an object before the beep will start triggering
MIN_DISTANCE_us = 20
MIN_DISTANCE_ir = 20
SENSOR_TOWARDS_GROUND = 2
AVG_HEIGHT_STAIRS = 15.0



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
        self.calibrate.append(cali_arr[0])
        self.calibrate.append(cali_arr[1])
        self.avg_height_below = self.calibrate_height_below(self.calibrate)


    def detect_obstacles(self,obstacles):
        for i,value in enumerate(obstacles):
            #print i, value
            if i != SENSOR_TOWARDS_GROUND:
                if value[0] <= MIN_DISTANCE_us or value[1] <= MIN_DISTANCE_ir :
                    alert_direction = self.index_to_direction[i]
                    print "obstacle at " + str(alert_direction)
                    #self.audio.play_sound(self.audio.sounds[alert_direction])
                    self.audio.play_sound(alert_direction)
                    if i == 1 or i == 2:
                        return True
            else:
                if value[0] <= self.avg_height_below or value[1] <= self.avg_height_below :
                    alert_direction = self.index_to_direction[i]
                    print "obstacle at " + str(alert_direction)
                    #self.audio.play_sound(self.audio.sounds[alert_direction])
                    self.audio.play_sound(alert_direction)
                    self.audio.play_sound('near_knee')
                elif (value[0] >= (self.avg_height_below + AVG_HEIGHT_STAIRS)) or value[1] >= (self.avg_height_below + AVG_HEIGHT_STAIRS):
                    self.audio.play_sound('step_below')
        return False




    def alt_route(self,distance):
        if not self.detect_ostacle_right(distance[3]):
            return True
        if not self.detect_ostacle_left(distance[0]):
            return True
        #if not self.detect_ostacle_behind(distance[3]):
            #return True
        self.audio.play_sound('around')
        return False


    def detect_ostacle_right(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            print "turn right"
            self.audio.play_sound('right')
            self.audio.play_sound('go')
        else:
            return True
        return False

    def detect_ostacle_left(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            print "turn left"
            self.audio.play_sound('left')
            self.audio.play_sound('go')
        else:
            return True
        return False

    def detect_ostacle_behind(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            print "turn around"
            self.audio.play_sound('around')
            self.audio.play_sound('go')
        else:
            return True
        return False

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