import subprocess
import time


# experimental result, is the minimum signal strength at 1 metre
MIN_DB_IS_A_METRE = -48

# number of cycles to check that it is higher than minimum dB
CYCLES = 3

# Mapping of router name to correct MAC address as the ones given are wrong
MAC_MAP = {'a8:9d:21:f3:86:40': 'arc-0214-a', # COM1-2 this and below
           'a8:9d:21:ee:0e:d0': 'arc-0212-a',
           'a8:9d:21:f3:93:f0': 'arc-0210-a',
           'a8:9d:21:f3:6f:f0': 'arc-0241-a',
           '84:b8:02:10:cf:e0': 'arc-0213-a',
           'a8:9d:21:c4:0d:50': 'arc-0207-a',
           'a8:9d:21:f3:86:a0': 'arc-0205-a',
           'a8:9d:21:f3:84:90': 'arc-0206-a',
           'a8:9d:21:f3:65:70': 'arc-0202-a',
           'a8:9d:21:f3:70:00': 'arc-0204-a',
           'a8:9d:21:74:09:70': 'arc-0201-a',
           'a8:9d:21:f3:6f:90': 'arc-0215-a', # COM2-2 this and below
           'a4:6c:2a:20:41:90': 'arc2-0261-a',
           'a8:9d:21:e4:6b:e0': 'arc-0229-a',
           'a4:6c:2a:20:3d:d0': 'arc2-0254-a',
           'a4:6c:2a:2e:de:60': 'arc2-0250-a',
           'a8:9d:21:44:05:70': 'arc2-0246-a',
           'a4:6c:2a:2e:dd:a0': 'arc2-0243-a',
           'a4:6c:2a:20:3f:50': 'arc2-0339-a', # COM2-3 this and below
           'a4:6c:2a:20:3e:e0': 'arc2-0318-a',
           '70:10:5c:7c:b2:60': 'arc2-0348-a', # actually arc2-0347-a, but arc2-0348-a on showmyway. actual 0348 near P2
           'b0:aa:77:42:ef:b0': 'arc-0324-a',
           'b0:aa:77:42:f1:10': 'arc-0334-a'}

class WifiFinder:

    def __init__(self):
        self.counter = 0
        pass
    
    # possible response when you are not near the access point
    # {'nodeName': 'arc-0234-a', 'MAC': 'AA:BB:CC:DD:EE:FF', 'strength': -53, 'is_near': False}
    # possible response when you are near the access point
    # {'nodeName': 'arc-0234-a', 'MAC': 'AA:BB:CC:DD:EE:FF', 'strength': -41, 'is_near': True}
    def is_within_range(self):
        signal = self.get_signal()
        if signal['MAC'] in MAC_MAP:
            signal['nodeName'] = MAC_MAP[signal['MAC']]
        else:
            signal['nodeName'] = ''     # if MAC address not found, put an empty string

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

