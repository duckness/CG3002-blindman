import math
#import matplotlib.pyplot as plt
from datetime import datetime
import requests
import json

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
NAVI_MAX = 25
WIFI_MAX = 250

#Mega inputs
INPUT_IMU      = "00"
INPUT_HEADING  = "01"
INPUT_SENSOR_1 = "10"
INPUT_SENSOR_2 = "11"
INPUT_SENSOR_3 = "12"
INPUT_SENSOR_4 = "13"
#POS magic
G = 9.81
HEADING_PER_UNIT = 22.5
HEADING_DRIFT = 45
DISTANCE_MULTIPLIER = 1.75
MAP_DISTANCE_MULTIPLIER = 1.8
MAP_DISTANCE_MULTIPLIER = 1.3
COUNT_MAX = 300
LIMIT_MULTIPLIER = 1.000001
# LIMIT_MULTIPLIER = 1.09
# LIMIT_MULTIPLIER = 1.01
AGGREGATE_LIMIT = 0
BUILDING = "COM1"
LEVEL = "2"

#calibrate obstacle
#OBSTACLE_CALIBRATION = 5

TIME_WAIT_AT_NODE = 5
TIME_WAIT_GOING_TO = 10
TIME_WAIT_TURN = 5
TIME_WAIT_GO = 10

#user input
COM1 = "1"
COM2 = "2"

class Logic:

    index_to_turn = {0: "left",
                     1: "right",
                     2: "go",
                     3: "stop",
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
        self.raw_heading = 999
        self.headings = []
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
        self.at_node_count = TIME_WAIT_AT_NODE
        self.going_to_node_count = TIME_WAIT_GOING_TO
        self.left_timer = TIME_WAIT_TURN
        self.right_timer = TIME_WAIT_TURN
        self.go_timer = TIME_WAIT_GO
        self.turn = -1
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
        self.count_wifi = 0
        self.count_navi = 0
        #init dist calculation
        self.r = 0
        self.limit = 0
        self.count_imu = 0
        self.threshold = 0
        self.avg_heading = 0
        self.distance = 0
        self.total_distance = 0 # total distance moved
        self.aggregate = 0
        self.x = []
        self.y = []
        self.isNewHeading = False
        self.map_x = []
        self.map_y = []
        self.ax = None
        self.line = None
        self.node_direction_index = 0

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

        ##set-up serial processing
        #self.serial_processor.wait_for_ready()
        print "Ready to recieve data from Mega"

        #TODO: self.audio.play_sound("calibrating")
        #do calibration here?
        # while(self.count_imu <= COUNT_MAX):
        #     self.get_mega_input()

        #setup timer
        #get current time in millsec
        #current_time = datetime.now().time()
        #self.loop_timer = current_time.microsecond

        # realtime mapping
        #self.getMaps()
        #plt.ion()
        #self.ax = plt.gca()
        #plt.plot(self.map_x, self.map_y, 'bo')
        #self.line, = self.ax.plot(self.x, self.y, 'ro-')

    def loop(self):
        destination = 0
        while(destination == 0):
            #read from mega at every possible second
            self.audio.sound_dequeue()
            self.get_mega_input()

            if(self.sensor_flag == True and self.count_imu > COUNT_MAX):
                #print self.sensors
                self.obstruction_flag = self.obstacle.detect_obstacles(self.sensors)
                if(self.obstruction_flag != self.obstacle.NO_OBSTACLES):
                    if(self.obstruction_flag == self.obstacle.OBSTACLE_STEP_DOWN):
                        self.audio.play_sound("step_below")
                        print "beware step down!"
                    elif(self.obstruction_flag == self.obstacle.OBSTACLE_STEP_UP):
                        self.audio.play_sound("near_knee")
                        print "beware step up!"
                    else:
                        print "stop"
                        self.audio.play_sound('stop')
                        self.reroute = self.obstacle.alt_route(self.sensors)
                self.sensor_flag = False

            #get current time in seconds
            #current_time = datetime.now().time()
            #micros = current_time.microsecond
            #print micros

            #every half second, calculate stuff/check wifi
            # if(abs(micros - self.loop_timer) >= LOOP_PERIOD):#
            #self.loop_timer = micros
            if(self.count_wifi == 100 and self.count_imu > COUNT_MAX):
                if (self.turn >= 0):
                    # print self.index_to_turn[self.turn], self.number
                    self.audio.play_sound(self.index_to_turn[self.turn])
                    # self.audio.play_number(self.number)

            if(self.count_navi >= NAVI_MAX and self.count_imu > COUNT_MAX):
                self.count_navi = 0
                print "navi"
                #self.loop_action = ACTION_WIFI
                #do navigation
                if (self.raw_heading == 999):
                    continue
                node_direction, turn_direction, walk_direction, destination = self.navigator.get_directions(self.position[0], self.position[1], self.raw_heading);
                self.node_direction_index = node_direction[0]
                print node_direction
                print turn_direction
                print self.raw_heading
                print "Walk distance: " + str(walk_direction)
                print "Destination Check: " + str(destination)
                print "-"
                if(self.obstruction_flag == self.obstacle.NO_OBSTACLES or self.obstruction_flag == self.obstacle.OBSTACLE_STEP_DOWN or self.obstruction_flag == self.obstacle.OBSTACLE_STEP_UP):
                    if(destination == 1):
                        print "you have reached dest"
                        self.audio.play_sound('stop')
                    else:
                        if(node_direction[0] == 0):
                            self.at_node_count += 1
                            self.going_to_node_count = TIME_WAIT_GOING_TO
                            if(self.at_node_count >= TIME_WAIT_AT_NODE):
                                #at node, play node ##
                                print "at node"
                                self.audio.play_number(node_direction[1], 'node')
                                self.at_node_count = 0
                        elif(node_direction[0] == 1):
                            self.going_to_node_count += 1
                            self.at_node_count = TIME_WAIT_AT_NODE
                            if(self.going_to_node_count >= TIME_WAIT_GOING_TO):
                                print "going to"
                                self.audio.play_number(node_direction[1])
                                self.going_to_node_count = 0

                        if(abs(turn_direction[1]) >= 46):
                            if(turn_direction[0] == 0): #turn left
                                # self.left_timer += 1
                                # self.go_timer = TIME_WAIT_GO
                                # self.right_timer = TIME_WAIT_TURN
                                # if(self.left_timer >= TIME_WAIT_TURN):
                                self.turn = 0
                                self.left_timer = 0
                            else:#turn right
                                # self.right_timer += 1
                                # self.go_timer = TIME_WAIT_GO
                                # self.left_timer = TIME_WAIT_TURN
                                # if(self.right_timer >= TIME_WAIT_TURN):
                                self.turn = 1
                                self.right_timer = 0
                        else:
                            # self.go_timer += 1
                            # self.left_timer = TIME_WAIT_TURN
                            # self.right_timer = TIME_WAIT_TURN
                            # if(self.go_timer >= TIME_WAIT_GO):
                            self.turn = 2
                            self.go_timer = 0
                else:
                    print "EH MAYBE BLOCK LAH EH MAYBE BLOCK LAH EH MAYBE BLOCK LAH EH MAYBE BLOCK LAH EH MAYBE BLOCK LAH EH MAYBE BLOCK LAH"
                    if(self.reroute == self.obstacle.BOTH_SIDE_FREE):
                        if(turn_direction[0] != 2):#follow map direction
                            print self.index_to_turn[turn_direction[0]]
                            self.audio.play_sound(self.index_to_turn[turn_direction[0]])
                        else:#turn right by default
                            self.audio.play_sound(self.index_to_turn[1])
                    elif(self.reroute == self.obstacle.NO_ALT_ROUTE):
                        print "around"
                        self.audio.play_sound('around')
                    else:
                        if(self.reroute == self.obstacle.LEFT_PATH_FREE):
                            turn = 0
                        else:
                            turn = 1
                        print self.index_to_turn[turn]
                        self.audio.play_sound(self.index_to_turn[turn])

            elif(self.count_wifi >= WIFI_MAX and self.count_imu > COUNT_MAX):
                print "wifi"
                self.count_wifi = 0
                #self.sensors[0][0] =  int(raw_input("Enter sensor 1 "))
                #self.sensors[0][1] =  int(raw_input("Enter sensor 1 "))
                #self.sensors[1][0] =  int(raw_input("Enter sensor 2 "))
                #self.sensors[1][1] =  int(raw_input("Enter sensor 2 "))
                #self.sensors[2][0] =  int(raw_input("Enter sensor 3 "))
                #self.sensors[2][1] =  int(raw_input("Enter sensor 3 "))
                #self.sensors[3][0] =  int(raw_input("Enter sensor 4 "))
                #self.sensors[3][1] =  int(raw_input("Enter sensor 4 "))
                #self.sensor_flag = True
                #self.position[0] = int(raw_input("Enter position x "))
                #self.position[1] = int(raw_input("Enter position y "))
                #self.raw_heading = float(raw_input("Enter heading "))
                print "wifi"
                self.signal = self.wifi_finder.is_within_range()
                print self.signal
                #check with navigation if wifi is true
                if (self.signal['is_near'] == True) :
                    print self.navigator.check_wifi(self.position[0], self.position[1], self.signal['nodeName'], 1.0)


            else:
                self.count_navi += 1
                self.count_wifi += 1

    def get_user_input(self):
        #TODO: have some sound for user input
        print "Please input building, level etc"
        self.audio.play_sound("trapped")
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

                   if self.count_imu <= COUNT_MAX:
                       self.calibrate_threshold()
                   else:
                       if self.r > self.limit:
                           self.distance += self.r * G * self.dt * self.dt * DISTANCE_MULTIPLIER * 100
                        #    print self.distance
               else:
                    pass

            # heading
            elif self.raw_data_arr[0] == INPUT_HEADING:
                if(self.parse_heading_input() == True):
                    # bundle readings of headings

                    if self.aggregate == AGGREGATE_LIMIT and self.count_imu > COUNT_MAX:
                            self.isNewHeading = True
                            self.aggregate = 0
                    else:
                        self.aggregate += 1
                        if (self.count_imu <= COUNT_MAX):
                            self.aggregate = 0

                    # 1 bundle awaiting after the calibration is done
                    if self.isNewHeading == True:
                        self.avg_heading = 0
                        self.headings.sort()

                        # aggregate the average headings
                        for heading in self.headings:
                            self.avg_heading += heading;
                        self.avg_heading /= len(self.headings)
                        # self.avg_heading += self.headings[len(self.headings)/2]
                        # self.avg_heading /= 2

                        # get the position based on previous position
                        offset = self.get_coord()
                        self.x.append(self.x[-1] + offset[0])
                        self.y.append(self.y[-1] + offset[1])
                        self.position[0] = self.x[-1]
                        self.position[1] = self.y[-1]

                        #update distance moved, reset for the next bundle
                        self.total_distance += self.distance
                        self.headings = []
                        self.distance = 0
                        # print self.total_distance
                        print "\t\t\t\t\tLOCATION", (self.x[-1], self.y[-1])
                        #self.line.set_xdata(self.x)
                        #self.line.set_ydata(self.y)
                        #self.ax.relim()
                        #plt.draw()
                        #plt.pause(0.0000001)

                    self.isNewHeading = False

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
                    #calibrate sensors
                    #tie obstacle calibration to imu calibration
                    if(self.count_imu < COUNT_MAX):
                    #if(self.obstacle_calibration_count < OBSTACLE_CALIBRATION):
                        self.obstacle.initial_calibration(self.sensors[1])
                        #self.obstacle_calibration_count += 1
                    self.sensor_flag = True
                else:
                    pass

            # sensor #3
            elif self.raw_data_arr[0] == INPUT_SENSOR_3:
                if(self.parse_sensor_3_input() == True):

                    #else:
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
                # tmp = float(self.values[0])
                # if (self.node_direction_index == 0 and self.count_imu > COUNT_MAX):
                #     self.raw_heading = tmp
                # elif (self.node_direction_index == 1 and self.count_imu > COUNT_MAX):
                #     min_heading = self.raw_heading-HEADING_PER_UNIT
                #     max_heading = self.raw_heading+HEADING_PER_UNIT
                #     if min_heading <= 0:
                #         min_heading += 360
                #     if max_heading >= 360:
                #         max_heading -= 360
                #     if tmp >= min_heading and tmp <= max_heading:
                #         self.raw_heading = tmp
                #     else:
                #         self.raw_heading = self.raw_heading
                # else:
                #     self.raw_heading = tmp
                #
                # multiplier = round(self.raw_heading/HEADING_PER_UNIT, 0)
                # aggregate_heading = multiplier * HEADING_PER_UNIT
                # self.raw_heading = aggregate_heading
                # self.headings.append(aggregate_heading)

                tmp = float(self.values[0])
                multiplier = round(tmp/HEADING_PER_UNIT, 0)
                tmp = multiplier * HEADING_PER_UNIT
                if (self.node_direction_index == 0 and self.count_imu > COUNT_MAX):
                    self.raw_heading = tmp
                elif (self.node_direction_index == 1 and self.count_imu > COUNT_MAX):
                    self.raw_heading = self.raw_heading
                else:
                    self.raw_heading = tmp

                self.headings.append(self.raw_heading)

                return True
            except ValueError:
                pass
        return False

    def parse_sensor_1_input(self):
         if len(self.values) == 2:
            try:
                self.sensors[0][0] = int(self.values[0])
                self.sensors[0][1] = int(self.values[1])
                return True
            except ValueError:
                pass
         return False

    def parse_sensor_2_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[1][0] = int(self.values[0])
                self.sensors[1][1] = int(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_3_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[2][0] = int(self.values[0])
                self.sensors[2][1] = int(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def parse_sensor_4_input(self):
        if len(self.values) == 2:
            try:
                self.sensors[3][0] = int(self.values[0])
                self.sensors[3][1] = int(self.values[1])
                return True
            except ValueError:
                pass
        return False

    def calibrate_threshold(self):
        if (self.count_imu < COUNT_MAX):
            if (self.count_imu == 0):
                print "Calibrating..."
            if self.r > 1.09:
                return
            self.count_imu += 1
            self.limit = max(self.limit, self.r)
        elif (self.count_imu == COUNT_MAX):
            self.count_imu += 1
            print "Ready!: ",
            print self.limit,
            self.limit *= LIMIT_MULTIPLIER
            print self.limit
        else:
            pass

    def north_from_Y(self):
        if self.northAt <= 180:
            return self.northAt
        elif self.northAt > 180:
            return -(360-self.northAt)

    def deg_from_Y(self):
        yOffset = self.north_from_Y()
        yDeg = self.avg_heading + yOffset
        # print heading, yOffset, yDeg
        if yDeg == 360:
            yDeg = 0;
        if yDeg < 0:
            yDeg += 360
        return yDeg

    def get_coord(self):
        angle = self.deg_from_Y()
        rad_angle = math.radians(angle)
        x = self.distance * round(math.sin(rad_angle),0) * MAP_DISTANCE_MULTIPLIER
        y = self.distance * round(math.cos(rad_angle),0) * MAP_DISTANCE_MULTIPLIER
        return (x,y)

    def getMaps(self):
        coord = []
        URL_STANDARD = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?"
        url = URL_STANDARD + "Building=" + self.building + "&Level=" + self.level

        try:
            REQUEST = requests.get(url)
            data = json.loads(REQUEST.text)
            info = data['info']
            if (info != None):
                local_map = data['map']
                for node in local_map:
                    self.map_x.append(int(node['x']))
                    self.map_y.append(int(node['y']))
            print url
        except:
            pass

#testing
logic = Logic()
logic.main()
