from audio import Audio
import operator


# the minimum distance in cm needed to an object before the beep will start triggering
MIN_DISTANCE = 20


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
                # todo: add checksum as well
                if sensors[1] == 0:  # 0 means out of range
                    continue
                elif sensors[1] <= MIN_DISTANCE:
                    alert_direction = self.index_to_direction[int(line[1])]
                    self.audio.play_sound(self.audio.sounds[alert_direction])
