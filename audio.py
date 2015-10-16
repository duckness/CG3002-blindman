import pygame

class Audio:

    sounds = {}

    def __init__(self):
        pygame.mixer.init()
        self.init_sounds()

    # TODO add new sounds
    def init_sounds(self):
        self.sounds = {'left': pygame.mixer.Sound("resources/turn_left.wav"),
                       'right': pygame.mixer.Sound("resources/turn_right.wav"),
                       'around': pygame.mixer.Sound("resources/turn_around.wav"),
                       'stop': pygame.mixer.Sound("resources/stop.wav"),
                       'go': pygame.mixer.Sound("resources/go.wav"),
                       'beep_left': pygame.mixer.Sound("resources/beep_left.wav"),
                       'beep_mid': pygame.mixer.Sound("resources/beep_mid.wav"),
                       'beep_right': pygame.mixer.Sound("resources/beep_right.wav"),
                       'trapped': pygame.mixer.Sound("resources/trapped.wav")
                       }

    # sound is a string, name of the sound file you want to play
    def play_sound(self, sound):
        self.sounds[sound].play(loops=0)

    # tell the user the node he currently is at. 
    def play_node(self, node_number):
        channel = sound.play('node')
        number = str(node_number)
        for c in number:
            channel.queue(c)


# a = Audio()
# a.play_sound('stop')
# time.sleep(20)

