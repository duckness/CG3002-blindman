import pygame
import time

class Audio:

    def __init__(self):
        self.sounds = {}
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

    # sound is a string, name of the sound file you want to play
    def play_sound(self, sound):
        self.sounds[sound].play(loops=0)

    # plays a number
    # CAN ONLY PLAY ONE OR TWO DIGIT NUMBERS
    def play_number(self, node_number):
        number = str(node_number)
        channel = self.sounds[number[0]].play(loops=0)
        if len(number) > 1:
            channel.queue(self.sounds[number[1]])


# a = Audio()
# a.play_sound('around')
# a.play_number(12)
# time.sleep(20)
