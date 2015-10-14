# NOTE: THIS IS NOT IN A CLASS FORMAT CAUSE IM TOO LAZY TO FIND OUT. SOMEONE SOS.
# This is the serial processing class
# All raw data from the Mega will be parsed into the corresponding variables
# Error checking is already done

import serial
import operator
import math
mega = serial.Serial(port='/dev/cu.usbserial-AH02MFHB', baudrate=115200, timeout=3)

def getChecksum(str):
        checksum = 0
        for i in xrange(0, len(str)):
            checksum = operator.xor(checksum, ord(str[i]))
        return checksum

def verifyData(data):
        if (len(data) != 3):
            return False
        chksum = 999
        try:
            chksum = int(data[2])
        except ValueError:
            chksum = 666
        return chksum == getChecksum(data[1])

def waitForReady():
        ready = False
        print "Waiting for ready signal"
        while (not ready):
            ready = "Begin: " in mega.readline()
            if (not ready):
                mega.write("RDY")

dt = 0.0
acc = [0, 0, 0]
gyro = [0, 0, 0]
magno = [0, 0, 0]
headings = [0, 0] # [current,previous]
pressure = 0
altitude = 0
temperature = 0
sensors = [[0, 0], [0, 0], [0, 0], [0, 0]] # [ultra,ir]

waitForReady()

print "Ready to recieve data from Mega"
while(True):
    raw_data = mega.readline().replace("\n", "")
    raw_data_arr = raw_data.split(", ")
    if (verifyData(raw_data_arr) == True):
        # values
        values = raw_data_arr[1].split("/")

        # imu
        if raw_data_arr[0] == "00":
            if len(values) == 13:
                try:
                    dt = float(values[0])
                    gyro[0] = float(values[1])
                    gyro[1] = float(values[2])
                    gyro[2] = float(values[3])
                    acc[0] = float(values[4])
                    acc[1] = float(values[5])
                    acc[2] = float(values[6])
                    magno[0] = float(values[7])
                    magno[1] = float(values[8])
                    magno[2] = float(values[9])
                    pressure = float(values[10])
                    altitude = float(values[11])
                    temperature = float(values[12])

                    #TODO: ADD CALIBRATION FOR LIMIT HERE
                except ValueError:
                    pass

        # heading
        elif raw_data_arr[0] == "01":
            if len(values) == 1:
                try:
                    headings[1] = headings[0]
                    headings[0] = float(values[0])
                except ValueError:
                    pass

        # sensor #1
        elif raw_data_arr[0] == "10":
            if len(values) == 2:
                try:
                    sensors[0][0] = float(values[0])
                    sensors[0][1] = float(values[1])
                except ValueError:
                    pass

        # sensor #2
        elif raw_data_arr[0] == "11":
            if len(values) == 2:
                try:
                    sensors[1][0] = float(values[0])
                    sensors[1][1] = float(values[1])
                except ValueError:
                    pass

        # sensor #3
        elif raw_data_arr[0] == "12":
            if len(values) == 2:
                try:
                    sensors[2][0] = float(values[0])
                    sensors[2][1] = float(values[1])
                except ValueError:
                    pass

        # sensor #4
        elif raw_data_arr[0] == "13":
            if len(values) == 2:
                try:
                    sensors[3][0] = float(values[0])
                    sensors[3][1] = float(values[1])
                except ValueError:
                    pass

        else:
            pass

    else:
        pass

mega.close
