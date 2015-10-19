import math
#import matplotlib.pyplot as plt
from datetime import datetime

from serial_processor import SerialProcessor
from navigator import Navigator
from obstacle import ObstacleCues
from user_input import UserInput
from audio import Audio
from wifi_finder import WifiFinder

#constants
#loop every this number of mricoseconds
LOOP_PERIOD = 500000 #500000 = 0.5 seconds
ACTION_NAVIGATION = 0
ACTION_WIFI = 1
#Mega inputs
INPUT_IMU      = "00"
INPUT_HEADING  = "01"
INPUT_SENSOR_1 = "10"
INPUT_SENSOR_2 = "11"
INPUT_SENSOR_3 = "12"
INPUT_SENSOR_4 = "13"
#POS magic
G = 9.81
MAX_CALIBRATION_COUNT = 200
MAGIC_THRESHOLD = 1.000001
MAGIC_DISTANCE = 1.3
MAGIC_HEADING = 0.75

#calibrate obstacle
#OBSTACLE_CALIBRATION = 5

#user input
COM1 = "1"
COM2 = "2"

class Logic:

    index_to_turn = {0: "left",
                     1: "right",
                     2: "go",
                     }

    def __init__(self):
        #init variables
        self.position = [0,0] # [0,0,0] #[x,y]
        self.northAt = 0
        self.building = ""
        self.level = ""
        self.start = 0
        self.end = 0
        self.values = []
        self.dt = 0.0
        self.acc = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.magno = [0, 0, 0]
        self.headings = [0, 0] # [current,previous]
        self.pressure = 0
        self.altitude = 0
        self.temperature = 0
        self.sensors = [[0, 0], [0, 0], [0, 0], [0, 0]] # [ultra,ir]
        self.sensor_flag = False
        self.reroute = False
        self.obstruction_flag = False
        self.signal = {}
        self.loop_timer = 0
        self.loop_action = 0
        #calibrate obstacle
        #self.done_calibration = False
        #self.obstacle_calibration_count = 0
        #init classes
        self.serial_processor = SerialProcessor()
        self.navigator = Navigator()
        self.obstacle = ObstacleCues()
        self.user_input = UserInput()
        self.audio = Audio()
        self.wifi_finder = WifiFinder()
        #init dist calculation
        self.r = 0
        self.count = 0
        self.threshold = 0
        self.short_distance = 0
        self.long_distance = 0 # total distance moved
        self.avg_heading = 0
        self.x = []
        self.y = []

    def main(self):
        self.setup()
        self.loop()
        self.serial_processor.close_mega()

    def setup(self):
        self.get_user_input()
        #input info into navigator
        check_map, check_start_node, check_end_node = self.navigator.calculate_path(self.building, self.level, self.start, self.end)
        #checking for validity
        while(check_map != 0 or check_start_node!=0 or check_end_node!=0): #invalid input
            self.get_user_input()
            check_map, check_start_node, check_end_node = self.navigator.calculate_path(self.building, self.level, self.start, self.end)

        self.northAt = self.navigator.get_northAt()
        # DUMMY
        #self.northAt = 315
        #get starting position
        self.position = self.navigator.get_position()
        # DUMMY
        #self.position = [0,0]
        self.x.append(self.position[0])
        self.y.append(self.position[1])

        #set-up serial processing
        self.serial_processor.wait_for_ready()
        print "Ready to recieve data from Mega"
        
        #do calibration here?
        while(self.count <= MAX_CALIBRATION_COUNT):
            self.get_mega_input()
        
        #setup timer
        #get current time in millsec
        current_time = datetime.now().time()
        self.loop_timer = current_time.microsecond

    def loop(self):
        while(1):
            #TODO: perhaps input a different timing scheme for this
            #read from mega at every possible second
            self.get_mega_input()
            
            if(self.sensor_flag == True):
                self.obstruction_flag = self.obstacle.detect_obstacles(self.sensors)
                if(self.obstruction_flag == True):
                    print "obstruction"
                    self.audio.play_sound('stop')
                    self.reroute = self.obstacle.alt_route(self.sensors)
                self.sensor_flag = False

            #get current time in seconds
            current_time = datetime.now().time()
            micros = current_time.microsecond
            #print micros

            #every half second, calculate stuff/check wifi
            if(abs(micros - self.loop_timer) >= LOOP_PERIOD):
                self.loop_timer = micros
                if(self.loop_action == ACTION_NAVIGATION):
                    print "navi"
                    self.loop_action = ACTION_WIFI
                    #do navigation
                    node_direction, turn_direction, walk_direction, destination = self.navigator.get_directions(self.position[0], self.position[1], self.headings[0]);
                    print node_direction
                    print turn_direction
                    print "Walk distance: " + str(walk_direction)
                    print "Destination Check: " + str(destination)
                    print "-"
                    if(self.obstruction_flag == False):
                        if(destination == 1):
                            #you have reached dest
                            self.audio.play_sound('stop')
                        else:
                            if(node_direction[0] == 0):
                                #at node, play node ##
                                self.audio.play_sound('node')
                                self.audio.play_number(node_direction[1])
                            #TODO: compare the angle and play turn left abit, turn right abit
                            self.audio.play_sound(self.index_to_turn[turn_direction[0]])           
                        
                elif(self.loop_action == ACTION_WIFI):
                    #self.sensors[0][0] =  raw_input("Enter sensor 1 ")
                    #self.sensors[0][1] =  raw_input("Enter sensor 1 ")
                    #self.sensors[1][0] =  raw_input("Enter sensor 2 ")
                    #self.sensors[1][1] =  raw_input("Enter sensor 2 ")
                    #self.sensors[2][0] =  raw_input("Enter sensor 3 ")
                    #self.sensors[2][1] =  raw_input("Enter sensor 3 ")
                    #self.sensors[3][0] =  raw_input("Enter sensor 4 ")
                    #self.sensors[3][1] =  raw_input("Enter sensor 4 ")
                    #self.sensor_flag = True
                    #self.position = [2000, 7000]
                    #self.headings = [315, 0]
                    print "wifi"
                    self.signal = self.wifi_finder.is_within_range()
                    #check with navigation if wifi is true
                    if (self.signal['is_near'] == True) :
                        self.navigator.check_wifi(position[0], position[1], i['MAC'], 1.0)
                        pass
                    self.loop_action = ACTION_NAVIGATION
                    #do wifi
                        #check wifi/position
                    pass

    def get_user_input(self):
        #TODO: have some sound for user input
        print "Please input building, level etc"
        #get building name from user input
        next_input = ''
        while(next_input == ''):           
            input = self.user_input.get_input()        
            #ensure input not empty
            while(input == ''):
                input = self.user_input.get_input()
            #check next input
            next_input = self.user_input.get_input()
        self.building = input        
        if(self.building == COM1):
            self.building = "COM1"
        if(self.building == COM2):
            self.building = "COM2"
        
        #get level from user input
        input = next_input
        next_input =  self.user_input.get_input()
        while(next_input == ''):
            input = self.user_input.get_input()        
            #ensure input not empty
            while(input == ''):
                input = self.user_input.get_input()
            next_input = self.user_input.get_input()
        self.level = input
        
        #get start
        input = next_input
        next_input =  self.user_input.get_input()
        while(next_input == ''):
            input = self.user_input.get_input()        
            #ensure input not empty
            while(input == ''):
                input = self.user_input.get_input()
            next_input = self.user_input.get_input()
        self.start = int(input)
        
        #get end
        input = next_input
        next_input =  self.user_input.get_input()
        while(next_input == ''):
            input = self.user_input.get_input()        
            #ensure input not empty
            while(input == ''):
                input = self.user_input.get_input()
            next_input = self.user_input.get_input()
        self.end = int(input)
        #self.building = raw_input("Please enter building name")
        #self.level = raw_input("Please enter level")
        #self.start = int(raw_input("Please enter start node"))
        #self.end = int(raw_input("Please enter end node"))
        print self.building, self.level, str(self.start), str(self.end)


    def get_mega_input(self):
        self.raw_data_arr = self.serial_processor.read_from_mega()
        # print self.raw_data_arr
        #dummy input
        # self.raw_data_arr = ["01","270"]
        if (self.serial_processor.verify_data(self.raw_data_arr) == True):
            # self.values
            self.values = self.raw_data_arr[1].split("/")

            # imu
            if self.raw_data_arr[0] == INPUT_IMU:
               if (self.parse_IMU_input() == True):
                   self.r = math.sqrt(self.acc[0]*self.acc[0] + self.acc[1]*self.acc[1] + self.acc[2]*self.acc[2])

                   if self.count <= MAX_CALIBRATION_COUNT:
                       self.calibrate_threshold()
                   else:
                       self.short_distance += self.r * G * self.dt * self.dt * MAGIC_DISTANCE
               else:
                    pass

            # heading
            elif self.raw_data_arr[0] == INPUT_HEADING:
                if(self.parse_heading_input() == True):
                    self.avg_heading = (self.headings[0] + self.headings[1]) / 2.0
                    if self.avg_heading < (MAGIC_HEADING * self.headings[0]):
                        self.avg_heading = self.headings[0]
                    offset = self.get_coord()
                    self.x.append(self.x[-1]+offset[0])
                    self.y.append(self.y[-1]+offset[1])
                    self.long_distance += self.short_distance
                    self.short_distance = 0
                    self.position[0] = self.x[-1]
                    self.position[1] = self.y[-1]

                    # if (len(self.x) == 50):
                    #     plt.figure(1)
                    #     plt.plot(self.x,self.y,"bo--")
                    #     plt.grid(True)
                    #     plt.show()
                else:
                    pass

            # sensor #1
            elif self.raw_data_arr[0] == INPUT_SENSOR_1:
               if(self.parse_sensor_1_input() == True):
                   self.sensor_flag = True
               else:
                   pass

            # sensor #2
            elif self.raw_data_arr[0] == INPUT_SENSOR_2:
                if(self.parse_sensor_2_input() == True):
                    self.sensor_flag = True
                else:
                    pass

            # sensor #3
            elif self.raw_data_arr[0] == INPUT_SENSOR_3:
                if(self.parse_sensor_3_input() == True):
                    #calibrate sensors
                    #tie obstacle calibration to imu calibration
                    if(self.count < MAX_CALIBRATION_COUNT):
                    #if(self.obstacle_calibration_count < OBSTACLE_CALIBRATION):            
                        self.obstacle.initial_calibration(sensors[2])
                        #self.obstacle_calibration_count += 1
                    else:
                        self.sensor_flag = True
                else:
                    pass

            # sensor #4
            elif self. raw_data_arr[0] == INPUT_SENSOR_4:
                if(self.parse_sensor_4_input() == True):
                    self.sensor_flag = True
                else:
                    pass

            else:
                pass

        else:
            pass

    def parse_IMU_input(self):
        if len(self.values) == 13:
            try:
                self.dt = float(self.values[0])
                self.gyro[0] = float(self.values[1])
                self.gyro[1] = float(self.values[2])
                self.gyro[2] = float(self.values[3])
                self.acc[0] = float(self.values[4])
                self.acc[1] = float(self.values[5])
                self.acc[2] = float(self.values[6])
                self.magno[0] = float(self.values[7])
                self.magno[1] = float(self.values[8])
                self.magno[2] = float(self.values[9])
                self.pressure = float(self.values[10])
                self.altitude = float(self.values[11])
                self.temperature = float(self.values[12])
                return True
            except ValueError:
                pass
        return False

    def parse_heading_input(self):
        if len(self.values) == 1:
            try:
                self.headings[1] = self.headings[0]
                self.headings[0] = float(self.values[0])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_1_input(self):
         if len(self.values) == 2:
            try:
                self.sensors[0][0] = float(self.values[0])
                self.sensors[0][1] = float(self.values[1])
                return True
            except ValueError:
                pass
         return False

    def parse_sensor_2_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[1][0] = float(self.values[0])
                self.sensors[1][1] = float(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_3_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[2][0] = float(self.values[0])
                self.sensors[2][1] = float(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_4_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[3][0] = float(self.values[0])
                self.sensors[3][1] = float(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def calibrate_threshold(self):
        if self.count < MAX_CALIBRATION_COUNT:
            if self.count == 0:
                print "Calibrating"
            self.count += 1
            self.threshold = max(self.threshold, self.r)
        elif self.count == MAX_CALIBRATION_COUNT:
            self.count += 1
            self.threshold *= MAGIC_THRESHOLD
            print "Ready! " + str(self.threshold)
        else:
            pass

    def north_from_Y(self):
        if self.northAt <= 180:
            return self.northAt
        elif self.northAt > 180:
            return -(360-self.northAt)

    def deg_from_Y(self):
        offset = self.north_from_Y()
        yDeg = self.avg_heading + offset
        if yDeg == 360:
            yDeg = 0;
        return yDeg

    def get_coord(self):
        angle = self.deg_from_Y()
        rad_angle = math.radians(angle)
        y = self.short_distance * math.sin(rad_angle)
        x = self.short_distance * math.cos(rad_angle)
        return (x,y)

#testing
logic = Logic()
logic.main()
