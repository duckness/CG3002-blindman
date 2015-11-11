import pygame
import time
from collections import deque


class Audio:

    def __init__(self):
        self.sounds = {}
        self.channels = {}
        self.number_queue = deque([])
        pygame.mixer.init()
        self.init_sounds()

    def init_sounds(self):
        self.sounds = {'left': pygame.mixer.Sound("resources/turn_left.wav"),
                       'right': pygame.mixer.Sound("resources/turn_right.wav"),
                       'around': pygame.mixer.Sound("resources/turn_around.wav"),
                       'stop': pygame.mixer.Sound("resources/stop.wav"),
                       'go': pygame.mixer.Sound("resources/go.wav"),
                       'beep_left': pygame.mixer.Sound("resources/beep_left.wav"),
                       'beep_mid': pygame.mixer.Sound("resources/beep_mid.wav"),
                       'beep_right': pygame.mixer.Sound("resources/beep_right.wav"),
                       'trapped': pygame.mixer.Sound("resources/trapped.wav"),
                       'near_knee': pygame.mixer.Sound("resources/obstacles_near_knee.wav"),
                       'step_below': pygame.mixer.Sound("resources/steps_below.wav"),
                       'node': pygame.mixer.Sound("resources/node.wav"),
                       '0': pygame.mixer.Sound("resources/0.wav"),
                       '1': pygame.mixer.Sound("resources/1.wav"),
                       '2': pygame.mixer.Sound("resources/2.wav"),
                       '3': pygame.mixer.Sound("resources/3.wav"),
                       '4': pygame.mixer.Sound("resources/4.wav"),
                       '5': pygame.mixer.Sound("resources/5.wav"),
                       '6': pygame.mixer.Sound("resources/6.wav"),
                       '7': pygame.mixer.Sound("resources/7.wav"),
                       '8': pygame.mixer.Sound("resources/8.wav"),
                       '9': pygame.mixer.Sound("resources/9.wav")
                       }
        self.channels = {'node': pygame.mixer.Channel(4),
                         'beep_left': pygame.mixer.Channel(5),
                         'beep_mid': pygame.mixer.Channel(6),
                         'beep_right': pygame.mixer.Channel(7)
                         }

    # sound is a string, name of the sound file you want to play
    def play_sound(self, sound):
        self.sounds[sound].play(loops=0)

    # plays a number, optionally with extra arguments before them
    # args takes in strings that represent sound files in the sounds dictionary
    def queue_sound(self, *args):
        for a in args:
            if str(a).isdigit():
                number = str(a)
                for c in number:
                    self.number_queue.append(c)
            else:
                self.number_queue.append(a)

    def play_beep(self, direction):
        self.channels[direction].queue(self.sounds[direction])

    def sound_dequeue(self):
        if self.channels['node'].get_queue() is None and len(self.number_queue) > 0:
            self.channels['node'].queue(self.sounds[self.number_queue.popleft()])


#a = Audio()
#a.play_sound("step_below")
#print "played"
#a.play_sound('around')
#a.play_number(12)
#for i in range(0,10):
    #a.play_beep('beep_mid')
    #a.sound_dequeue()
    #time.sleep(0.2)
#time.sleep(20)
