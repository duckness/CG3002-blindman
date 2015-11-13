from matrix_key import MatrixKey
from audio import Audio


class lol:
    def __init__(self):
        pass

    def read_input(self):
        inp = ''
        while (len(inp) != 1):
            inp = raw_input('Pretend you press a key on keypad:')
            if (len(inp)!=1):
                print 'fuck you. input one character.'
        return inp

class UserInput:

    def __init__(self):
        # self.kp = lol()
        self.audio = Audio()
        self.kp = MatrixKey()

    def get_input(self):
        # Loop while waiting for a keypress
        inp =''
        while (len(inp)<1 or inp[-1]!='#'):
            digit = None
            while digit == None:
                # digit = self.kp.getKey()
                digit = self.kp.read_input()
            if(digit=='*'):
                self.audio.play_sound('beep_left')
                inp =''
            else:
                if(digit=='#'):
                    self.audio.play_sound('beep_right')
                else:
                    self.audio.play_sound(digit)
                inp += digit
        return inp[:-1]
