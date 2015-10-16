from audio import Audio
import operator


# the minimum distance in cm needed to an object before the beep will start triggering
MIN_DISTANCE_us = 20
MIN_DISTANCE_ir = 20



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

    def detect_obstacles(self,obstaclses):
        for i,value in enumerate(obstaclses):
            if value[1] <= MIN_DISTANCE_us or value[2] <= MIN_DISTANCE_ir :
                alert_direction = self.index_to_direction[i]
                self.audio.play_sound(self.audio.sounds[alert_direction])
                if i == 1 or i == 2:
                    self.alt_route(obstaclses)


    def alt_route(self,distance):
        if not self.detect_ostacle_right(distance[3]):
            return True
        if not self.detect_ostacle_left(distance[0]):
            return True
        #if not self.detect_ostacle_behind(distance[3]):
            #return True
        self.audio.play_sound(self.audio.sounds['trapped'])
        return False


    def detect_ostacle_right(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            self.audio.play_sound(self.audio.sounds['right'])
            self.audio.play_sound(self.audio.sounds['go'])
        else:
            return True
        return False

    def detect_ostacle_left(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            self.audio.play_sound(self.audio.sounds['left'])
            self.audio.play_sound(self.audio.sounds['go'])
        else:
            return True
        return False

    def detect_ostacle_behind(self,distance):
        if not (distance[0] <= MIN_DISTANCE_us or distance[1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            self.audio.play_sound(self.audio.sounds['around'])
            self.audio.play_sound(self.audio.sounds['go'])
        else:
            return True
        return False


