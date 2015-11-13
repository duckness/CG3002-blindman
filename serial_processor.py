# This is the serial processing class
# Read raw data from serial
# Error checking is already done

import serial
import operator
import math
# mega = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=3)
mega = serial.Serial(port='/dev/cu.usbserial-AH02MFHB', baudrate=115200, timeout=3)
# mega = open('COM1_2_10_COM1_2_34_Serial1447391973.38_.txt','r')

class SerialProcessor:
    def get_checksum(self, str):
            checksum = 0
            for i in xrange(0, len(str)):
                checksum = operator.xor(checksum, ord(str[i]))
            return checksum

    def verify_data(self, data):
            if (len(data) != 3):
                return False
            chksum = 999
            try:
                chksum = int(data[2])
            except ValueError:
                chksum = 666
            return chksum == self.get_checksum(data[1])

    def wait_for_ready(self):
            ready = False
            print "Waiting for ready signal"
            while (not ready):
                ready = "Begin: " in mega.readline()
                if (not ready):
                    mega.write("RDY")

    def read_from_mega(self):
        raw_data = mega.readline().replace("\n", "")
        raw_data_arr = raw_data.split(", ")
        return raw_data_arr

    def close_mega(self):
        mega.close
