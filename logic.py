from datetime import datetime

from serial_processor import SerialProcessor
from navigator import Navigator
from obstacle import ObstacleCues
from user_input import UserInput
from audio import Audio
from wifi_finder import WifiFinder

#constants
#loop every this number of mricoseconds
LOOP_PERIOD = 500000 #500 = 0.5 seconds
ACTION_NAVIGATION = 0
ACTION_WIFI = 1
#Mega inputs
INPUT_IMU      = "00"
INPUT_HEADING  = "01"
INPUT_SENSOR_1 = "10"
INPUT_SENSOR_2 = "11"
INPUT_SENSOR_3 = "12"
INPUT_SENSOR_4 = "13"

class Logic:

    def __init__(self):
        #init variables
        self.position = [0,0,0]
        self.northAt = 0
        self.building = ""
        self.level = ""
        self.dt = 0.0
        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.magno = [0, 0, 0]
        self.headings = [0, 0] # [current,previous]
        self.pressure = 0
        self.altitude = 0
        self.temperature = 0
        self.sensors = [[0, 0], [0, 0], [0, 0], [0, 0]] # [ultra,ir]
        self.signal = ""
        self.loop_timer = 0
        self.loop_action = 0
        #self.raw_data_arr = ["",""]
        #init classes
        self.serial_processor = SerialProcessor()
        self.navigator = Navigator()
        self.obstacle = ObstacleCues()
        self.user_input = UserInput()
        self.audio = Audio()
        self.wifi_finder = WifiFinder()
        #init dist calculation
        

    def main(self):
        self.setup()
        self.loop()
        self.serial_processor.close_mega()
       
    def setup(self):
        #get building name etc from user input
            #self.user_input.get_input()
        #input info into navigator
            #self.navigator.retrieve_map(input info)
            #self.northAt = self.navigator.get_northAt
        #get starting position
            #self.position = self.navigator.get_position
        
        #setup timer    
        #get current time in millsec
        current_time = datetime.now().time()
        self.loop_timer = current_time.microsecond   
        
        #set-up serial processing
        #waitForReady()
        #print "Ready to recieve data from Mega"

    def loop(self):
        while(1):
            #TODO: perhaps input a different timing scheme for this
            #read from mega at every possible second 
            self.get_mega_input()
            #get current time in seconds
            current_time = datetime.now().time()
            mricos = current_time.microsecond  
            #print mricos

            #every half second, calculate stuff/check wifi
            if(abs(mricos - self.loop_timer) >= LOOP_PERIOD):
                self.loop_timer = mricos
                if(self.loop_action == ACTION_NAVIGATION):
                    #print "navi"
                    self.loop_action = ACTION_WIFI                    
                    #do navigation
                        #directions = self.navigator.get_directions()
                    #play sounds
                        #self.audio.play_sound(directions)
                elif(self.loop_action == ACTION_WIFI):
                    #print "wifi"
                    #self.signal = self.wifi_finder.is_within_range()
                    #print signal
                    #check with navigation if wifi is true
                    self.loop_action = ACTION_NAVIGATION                    
                    #do wifi
                        #check wifi/position
                

    def get_mega_input(self):
        #self.raw_data_arr = self.serial_processor.read_from_mega()
        #print self.raw_data_arr
        #dummy input
        self.raw_data_arr = ["01","270"]
        if (self.serial_processor.verify_data(self.raw_data_arr) == True):
            # values
            values = self.raw_data_arr[1].split("/")

            # imu
            if self.raw_data_arr[0] == INPUT_IMU:
               if (self.parse_IMU_input() == True):
                   #TODO: ADD CALIBRATION FOR LIMIT HERE
                   #TODO: self.position = dist calculation
                   pass
            # heading
            elif self.raw_data_arr[0] == INPUT_HEADING:
                if(self.parse_heading_input() == True):
                    #TODO: not sure what heading will be used for. dist cal?
                    pass

            # sensor #1
            elif self.raw_data_arr[0] == INPUT_SENSOR_1:
               if(self.parse_sensor_1_input() == True):
                   pass

            # sensor #2
            elif self.raw_data_arr[0] == INPUT_SENSOR_2:
                if(self.parse_sensor_2_input() == True):
                    pass

            # sensor #3
            elif self.raw_data_arr[0] == INPUT_SENSOR_3:
                if(self.parse_sensor_3_input() == True):
                    pass

            # sensor #4
            elif self. raw_data_arr[0] == INPUT_SENSOR_4:
                if(self.parse_sensor_4_input() == True):
                    pass

            else:
                pass

        else:
            pass

    def parse_IMU_input(self):
        if len(values) == 13:
            try:
                self.dt = float(values[0])
                self.gyro[0] = float(values[1])
                self.gyro[1] = float(values[2])
                self.gyro[2] = float(values[3])
                self.acc[0] = float(values[4])
                self.acc[1] = float(values[5])
                self.acc[2] = float(values[6])
                self.magno[0] = float(values[7])
                self.magno[1] = float(values[8])
                self.magno[2] = float(values[9])
                self.pressure = float(values[10])
                self.altitude = float(values[11])
                self.temperature = float(values[12])
                return True
            except ValueError:
                pass
        return False    

    def parse_heading_input(self):
        if len(values) == 1:
            try:
                self.headings[1] = headings[0]
                self.headings[0] = float(values[0])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_1_input(self):
         if len(values) == 2:
            try:
                self.sensors[0][0] = float(values[0])
                self.sensors[0][1] = float(values[1])
                return True
            except ValueError:
                pass
         return False

    def parse_sensor_2_input(self):
        if len(values) == 2:
            try:
                self.sensors[1][0] = float(values[0])
                self.sensors[1][1] = float(values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_3_input(self):
        if len(values) == 2:
            try:
                self.sensors[2][0] = float(values[0])
                self.sensors[2][1] = float(values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_4_input(self):
        if len(values) == 2:
            try:
                self.sensors[3][0] = float(values[0])
                self.sensors[3][1] = float(values[1])
                return True
            except ValueError:
                pass
        return False
#testing
logic = Logic()
logic.main()