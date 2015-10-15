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
                    for i in range(0,3):
                        if distance[i][1] <= MIN_DISTANCE_us or distance[i][2] <= MIN_DISTANCE_ir :
                            alert_direction = self.index_to_direction[int(line[1])]
                            self.audio.play_sound(self.audio.sounds[alert_direction])
                            self.alt_route(distance)

                """
                if sensors[2] <= MIN_DISTANCE:
                    alert_direction = self.index_to_direction[int(line[1])]
                    self.audio.play_sound(self.audio.sounds[alert_direction])
                """


    def alt_route(self,distance):

        if not (distance[1][0] <= MIN_DISTANCE_us or distance[1][1] <= MIN_DISTANCE_ir): # should base on navigation between left and right
            self.audio.play_sound(self.audio.sounds['right'])
            self.audio.play_sound(self.audio.sounds['go'])
            return
        if not (distance[2][0] <= MIN_DISTANCE_us or distance[2][1] <= MIN_DISTANCE_ir):
            self.audio.play_sound(self.audio.sounds['left'])
            self.audio.play_sound(self.audio.sounds['go'])
            return
        if not (distance[3][0] <= MIN_DISTANCE_us or distance[3][1] <= MIN_DISTANCE_ir):
            self.audio.play_sound(self.audio.sounds['around'])
            self.audio.play_sound(self.audio.sounds['go'])
            return
        self.audio.play_sound(self.audio.sounds['trapped'])
        return


