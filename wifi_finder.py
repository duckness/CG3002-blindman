import subprocess
import time


# experimental result, is the minimum signal strength at 1 metre
MIN_DB_IS_A_METRE = -48

# number of cycles to check that it is higher than minimum dB
CYCLES = 3


class WifiFinder:

    counter = 0

    def __init__(self):
        pass

    def is_within_range(self):
        signal = self.get_signal()
        if signal['strength'] > MIN_DB_IS_A_METRE:
            self.counter += 1
        else:
            self.counter = 0
        if self.counter < CYCLES:
            signal['is_near'] = False
        else:
            signal['is_near'] = True
        return signal

    def get_signal(self):
        strn = self.ping_router().splitlines()
        signal = {'strength': -int(''.join(x for x in strn[1] if x.isdigit())),
                  'MAC': strn[0].split()[2]
                  }
        return signal

    # OSX does NOT have wavemon
    # only works on Linux, install wavemon if not installed
    # sudo apt-get install -y wavemon
    def ping_router(self):
        return subprocess.check_output("wavemon -i wlan0 -d | grep '\(SNR:\|access point:\)'", shell=True)


#w = WifiFinder()
#while True:
#    print w.is_within_range()
#    time.sleep(1)
