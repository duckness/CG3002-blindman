#from membraneMatrix import keypad

class lol:
    def __init__(self):
        pass

    def getKey(self):
        inp = ''
        while (len(inp) != 1):
            inp = raw_input('Pretend you press a key on keypad:')
            if (len(inp)!=1):
                print 'fuck you. input one character.'
        return inp

class UserInput:

    def __init__(self):
        self.kp = lol()
        #self.kp = membraneMatrix.keypad(columnCount = 3)

    def get_input(self):
        # Loop while waiting for a keypress
        inp =''
        while (len(inp)<1 or inp[-1]!='#'):
            digit = None
            while digit == None:
                digit = self.kp.getKey()
            inp += digit
        return inp[:-1]