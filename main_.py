# required imports
import math
from serial_processor import SerialProcessor
from navigator import Navigator
from obstacle_v2 import ObstacleCues
from user_input import UserInput
from audio import Audio

# debugging imports
# import matplotlib.pyplot as plt
import requests
import json
import sys
from time import time

# constants
# hardware id
ID_IMU              = '00'
ID_HEADING          = '01'
ID_SENSOR_1         = '10'
ID_SENSOR_2         = '20'
ID_SENSOR_3         = '30'
ID_SENSOR_4         = '40'
# limits
MIN_CALIBRATE       = -50
MAX_CALIBRATE       = 300
MAX_NAVIGATION      = 250
MIN_TURN_ANGLE      = 20
MAX_OBSTACLE        = 100
MAX_ALTITUDE        = 10
# multiplier
MULTIPLIER_LIMIT    = 1.01
MULTIPLIER_G        = 981 # cm
MULTIPLIER_DISTANCE = 2
MULTIPLIER_MAP_C1   = 1
MULTIPLIER_MAP_C2   = 1
MULTIPLIER_HEADING  = 22.5
# user input
MAP_COM1            = '1'
MAP_COM2            = '2'
# inter-map nodes
COM1_to_COM2        = (31, 1)
COM2_2_to_COM2_3    = (16, 11)
# buffers
NODE_BUFFER         = 0.05

class Main:

    # initialize class
    def __init__(self):
        # modules
        self.processor      = SerialProcessor()
        self.navigator      = Navigator()
        self.obstacle       = ObstacleCues()
        self.user_input     = UserInput()
        self.audio          = Audio()
        # map
        self.north_at       = 0
        self.building_start = ''
        self.building_dest  = ''
        self.temp_building  = ''
        self.level_start    = ''
        self.level_dest     = ''
        self.temp_level     = ''
        self.start          = ''
        self.temp_start     = ''
        self.temp_end       = ''
        self.end_dest       = ''
        self.position       = [0,0]
        self.x              = []
        self.y              = []
        # hardware
        self.dt             = 0
        self.acc            = [0,0,0]
        self.gyro           = [0,0,0]
        self.magno          = [0,0,0]
        self.heading        = 999
        self.pressure       = 0
        self.prev_altitude  = None
        self.altitude       = None
        self.temp           = 0
        self.sensors        = [[0,0],[0,0],[0,0],[0,0]]
        # calibration
        self.calibrate      = MIN_CALIBRATE
        self.limit          = 0
        self.node_shift     = False
        # calculations
        self.r              = 0
        self.distance       = 0
        # navigation
        self.navigation     = 0
        self.node_dir       = None
        self.prev_node      = None
        self.obstacle_count = 0
        # debugging
        self.log            = None
        self.map_x          = []
        self.map_y          = []
        self.axis           = None
        self.line           = None
        self.distance_t     = 0

    def switching_map(self):
        #COM1 to COM1 / COM2 to COM2
        if self.building_start == self.building_dest:
            #COM1-2 to COM1-2 / COM2-2 to COM2-2 / COM2-3 to COM2-3
            if self.level_start == self.level_dest:
                self.temp_end = self.end_dest
            else:
                #COM2-2 to COM2-3 / COM2-3 to COM2-2
                self.temp_building = "COM2"
                if self.level_dest == '3':
                    #COM2-2 to COM2-3
                    self.temp_end = COM2_2_to_COM2_3[0]
                    self.temp_start = COM2_2_to_COM2_3[1]
                    self.temp_level = '3'
                else:
                    #COM2-3 to COM2-2
                    self.temp_end = COM2_2_to_COM2_3[1]
                    self.temp_start = COM2_2_to_COM2_3[0]
                    self.temp_level = '2'
        #COM1 to COM2 / COM2 to COM1
        else:
            #COM1-2 to COM2-2 / COM1-2 to COM2-3
            if self.building_start == "COM1":
                #route to COM2-2 first
                self.temp_end = COM1_to_COM2[0]
                self.temp_start = COM1_to_COM2[1]
                self.temp_building = "COM2"
                self.temp_level = '2'
            #COM2-2 to COM1-2 / COM2-3 to COM1-2
            else:
                #COM2-2 to COM1-2
                if self.level_dest == self.level_start:
                    self.temp_end = COM1_to_COM2[1]
                    self.temp_start = COM1_to_COM2[0]
                    self.temp_building = "COM1"
                    self.temp_level = '2'
                #COM2-3 to COM1-2
                else:
                    #route to COM2-2 first
                    self.temp_end = COM2_2_to_COM2_3[1]
                    self.temp_start = COM2_2_to_COM2_3[0]
                    self.temp_building = "COM2"
                    self.temp_level = '2'

    # setup
    def setup(self):
        # input map info / all must be 0
        self.get_map_input()
        self.switching_map()
        self.navigator.calculate_path(self.building_start, self.level_start, self.start, self.temp_end)
        print 'temp_end: ' + str(self.temp_end)

        # setup map
        self.north_at = self.navigator.get_northAt()
        self.position = self.navigator.get_position()
        self.x.append(self.position[0])
        self.y.append(self.position[1])

        # ready signal
        print 'System Ready.'

        # debugging
        self.log = open(sys.path[0] + "/"+self.building_start+'_'+self.level_start+'_'+self.start+'_'+self.building_dest+'_'+self.level_dest+'_'+self.end_dest+'_'+"Serial"+str(time())+'_'".txt", 'w')
        # self.get_map()
        # plt.plot(self.map_x, self.map_y, 'bo')
        # plt.ion()
        # self.axis = plt.gca()
        # self.line, = self.axis.plot(self.x, self.y, 'ro-')


    # get map input
    def get_map_input(self):
        print 'Input map information'
        self.audio.queue_sound('trapped')

        # parsing of user input
        # 0: building / 1: level / 2: start / 3: end
        # expected behavior:
        #   keypress get sent when '#' is pressed. set to corresponding
        #   variable. increment to next variable. if blank is sent, ignore
        #   but keep the variable index.
        input_id = 0
        keypress = ''

        while input_id < 6:
            # debugging
            # self.building_start = 'COM1'
            # self.level_start = '2'
            # self.start = '10'
            # self.building_dest = 'COM1'
            # self.level_dest = '2'
            # self.end_dest = '34'
            # break

            keypress = self.user_input.get_input()
            if keypress == '':
                continue

            if input_id == 0:
                self.building_start = keypress
                # defaults
                if self.building_start == MAP_COM1:
                    self.building_start = 'COM1'
                elif self.building_start == MAP_COM2:
                    self.building_start = 'COM2'
            elif input_id == 1:
                self.level_start = keypress
            elif input_id == 2:
                self.start = keypress
            elif input_id == 3:
                self.building_dest = keypress
                if self.building_dest == MAP_COM1:
                    self.building_dest = 'COM1'
                elif self.building_dest == MAP_COM2:
                    self.building_dest = 'COM2'
            elif input_id == 4:
                self.level_dest = keypress
            elif input_id == 5:
                self.end_dest = keypress
            else:
                input_id = -1

            input_id += 1

        print 'User Input: ',
        print  self.building_start, self.level_start, str(self.start), self.building_dest, self.level_dest, str(self.end_dest)

    # get serial data
    def get_mega_data(self):
        # get serial information in array format
        raw_data = self.processor.read_from_mega()

        parse_status = False
        if self.processor.verify_data(raw_data) == True:
            data_id = raw_data[0]
            raw_values = raw_data[1].split('/')

            # data processing
            if data_id == ID_IMU:
                parse_status = self.process_imu(raw_values)
            elif data_id == ID_HEADING:
                parse_status = self.process_heading(raw_values)
            else:
                parse_status = self.process_sensor(data_id, raw_values)

            # debugging
            # print raw_data
            self.log.write(raw_data[0] + ', ' + raw_data[1] + ', ' + raw_data[2] + '\n')
            self.log.flush

        return parse_status

    # imu processing
    def process_imu(self, raw_values):
        # ensure data integrity
        if len(raw_values) != 13:
            return False

        self.prev_altitude = self.altitude
        # parsing of raw_values
        try:
            self.dt         = float(raw_values[0])
            self.gyro[0]    = float(raw_values[1])
            self.gyro[1]    = float(raw_values[2])
            self.gyro[2]    = float(raw_values[3])
            self.acc[0]     = float(raw_values[4])
            self.acc[1]     = float(raw_values[5])
            self.acc[2]     = float(raw_values[6])
            self.magno[0]   = float(raw_values[7])
            self.magno[1]   = float(raw_values[8])
            self.magno[2]   = float(raw_values[9])
            self.pressure   = float(raw_values[10])
            self.altitude   = float(raw_values[11])
            self.temp       = float(raw_values[12])
        except ValueError:
            return False

        # calculations
        self.r = math.sqrt(self.acc[0]*self.acc[0] + self.acc[1]*self.acc[1] + self.acc[2]*self.acc[2])

        # calibration
        if self.calibrate <= MAX_CALIBRATE and self.calibrate >= 0:
            tmp_r = self.r * MULTIPLIER_LIMIT
            self.limit = max(self.limit, tmp_r)
        elif self.calibrate > MAX_CALIBRATE:
            if self.r > self.limit:
                # multiplier renewal
                if self.building_start == 'COM1':
                    if self.prev_node == [5603,1787]:
                        self.distance += self.r * MULTIPLIER_G * self.dt * self.dt * MULTIPLIER_DISTANCE * MULTIPLIER_MAP_C1*0.8
                    else:
                        self.distance += self.r * MULTIPLIER_G * self.dt * self.dt * MULTIPLIER_DISTANCE * MULTIPLIER_MAP_C1
                else:
                    self.distance += self.r * MULTIPLIER_G * self.dt * self.dt * MULTIPLIER_DISTANCE * MULTIPLIER_MAP_C2
                # climb stairs
                if abs(self.altitude - self.prev_altitude) > MAX_ALTITUDE:
                    self.distance = 0
        else:
            pass

        return True

    # heading processing
    def process_heading(self, raw_values):
        # ensure data integrity
        if len(raw_values) != 1:
            return False

        # parsing of raw_values
        try:
            tmp = float(raw_values[0])
            self.heading = tmp
        except ValueError:
            return False

        if self.calibrate <= MAX_CALIBRATE:
            return True

        # position
        pos_offset = self.process_position()
        self.x.append(self.x[-1] + pos_offset[0])
        self.y.append(self.y[-1] + pos_offset[1])
        self.position[0] = self.x[-1]
        self.position[1] = self.y[-1]

        # debugging
        # self.line.set_xdata(self.x)
        # self.line.set_ydata(self.y)
        # self.axis.relim()
        # plt.draw()
        # plt.pause(0.0000001)
        self.distance_t += self.distance
        # print self.distance_t

        # prepare for new set of heading information
        self.distance = 0

        return True

    # sensors processing
    def process_sensor(self, data_id, raw_values):
        # ensure data integrity
        if len(raw_values) != 2:
            return False

        # parsing of raw_values
        try:
            index = int(data_id)%10
            self.sensors[index][0] = int(raw_values[0])
            tmp = int(raw_values[1])
            if tmp > 160:
                tmp = 160
            elif tmp < 20:
                tmp = 20
            if index == 1:
                self.sensors[index][1] *= 0.45
                self.sensors[index][1] += tmp*0.55
                self.sensors[index][1] += 0.5
                self.sensors[index][1] = int(self.sensors[index][1])
            else:
                self.sensors[index][1] = tmp
            # self.sensors[index][1] = tmp
            if (index == 1 and self.calibrate < MAX_CALIBRATE and self.calibrate >= 0):
                self.sensors[index][1] = tmp
                self.obstacle.initial_calibration(self.sensors[1])

        except ValueError:
            return False

        return True

    # position processing
    def process_position(self):
        # north offset from y-axis
        offset_y_angle = self.north_at
        if self.north_at > 180:
            offset_y_angle = - (360 - self.north_at)

        # offset from y-axis
        y_degree = self.heading + offset_y_angle
        if y_degree == 360:
            y_degree = 0
        elif y_degree < 0:
            y_degree += 360

        # calculate position from heading
        y_degree_rad = math.radians(y_degree)
        # print y_degree_rad
        x = self.distance * round(math.sin(y_degree_rad),0)
        y = self.distance * round(math.cos(y_degree_rad),0)

        return (x,y)

    # main: where the money is
    def main(self):
        # setup everything
        self.setup()

        destination = 0
        while destination == 0:
            # play sound
            self.audio.sound_dequeue()

            # read serial
            if self.get_mega_data() == False:
                continue

            # calibration
            if self.calibrate <= MAX_CALIBRATE:
                if self.calibrate == 0:
                    print 'Start Calibration'

                if self.calibrate == MAX_CALIBRATE:
                    print 'End Calibration'
                    print 'Limit: ', self.limit
                    self.navigation = MAX_NAVIGATION+1

                self.calibrate += 1
                continue

            # obstacle
            if self.obstacle_count > 0:
                self.obstacle_count -= 1

            obstacle_detected = self.obstacle.detect_obstacles(self.sensors)
            if obstacle_detected != self.obstacle.NO_OBSTACLES and self.obstacle_count == 0:
                # start obstacle counter + delay node update
                self.obstacle_count = MAX_OBSTACLE
                # self.navigation -= self.navigation/4

                # print self.sensors[1][1]
                if obstacle_detected == self.obstacle.OBSTACLE_STEP_DOWN:
                    print 'Beware: Step DOWN'
                    self.audio.queue_sound('step_below')
                    # self.navigation += self.navigation/2
                    pass
                elif obstacle_detected == self.obstacle.OBSTACLE_STEP_UP:
                    print 'Beware: Near KNEE'
                    self.audio.queue_sound('near_knee')
                else:
                    print 'Beware: STOP'
                    self.audio.queue_sound('stop')

            # navigation
            self.node_dir, turn_dir, walk_dir, destination = self.navigator.get_directions(self.position[0], self.position[1], self.heading)

            # check if at node
            if self.node_dir[0] == 0 and self.node_shift == False:
                print ''
                print 'Reached node'
                print 'Heading: ', self.heading
                # print 'Walk: ', str(walk_dir)
                print ''
                self.audio.queue_sound('node', self.node_dir[1])
                pass

            # node shift into the right coordinates
            if self.node_dir[0] == 0 or destination == 1:
                tmp = self.navigator.get_node_position()
                node = [0, 0]
                node[0] = tmp[0]
                node[1] = tmp[1]

                if self.prev_node == None:
                    self.prev_node = node
                else:
                    if self.prev_node[0] == node[0]:
                        node[1] += (self.prev_node[1] - node[1])*NODE_BUFFER
                    elif self.prev_node[1] == node[1]:
                        node[0] += (self.prev_node[0] - node[0])*NODE_BUFFER
                    self.prev_node[0] = tmp[0]
                    self.prev_node[1] = tmp[1]

                if self.node_shift == False:
                    self.x.append(node[0])
                    self.y.append(node[1])
                    self.position[0] = self.x[-1]
                    self.position[1] = self.y[-1]
                    # self.line.set_xdata(self.x)
                    # self.line.set_ydata(self.y)
                    # self.axis.relim()
                    # plt.draw()
                    # plt.pause(0.0000001)
                    self.node_shift = True
            else:
                self.node_shift = False

            # reached destination
            if destination == 1:
                print "Reached end of map"
                #check if we have reached actual dest
                if self.building_start == self.building_dest and self.level_start == self.level_dest:
                    break
                else:
                    print "Changing map"
                    #reset destination
                    destination = 0
                    #update current map
                    self.building_start = self.temp_building
                    self.level_start = self.temp_level
                    self.start = self.temp_start
                    #get new temp_end
                    self.switching_map()
                    print  self.building_start, self.level_start, self.start, self.temp_end
                    #get new map
                    self.navigator.calculate_path(self.building_start, self.level_start, self.start, self.temp_end)
                    # reset map
                    self.north_at = self.navigator.get_northAt()
                    self.position = self.navigator.get_position()
                    self.x = []
                    self.y = []
                    self.x.append(self.position[0])
                    self.y.append(self.position[1])
                    print self.north_at, self.x, self.y, self.building_start, self.level_start
                    print self.navigator.get_position()
                    # get new map
                    # self.get_map()
                    # plt.close()
                    # plt.plot(self.map_x, self.map_y, 'bo')
                    # plt.ion()
                    # self.axis = plt.gca()
                    # self.line, = self.axis.plot(self.x, self.y, 'ro-')
                    continue

            # not at node, periodic update
            if self.navigation >= MAX_NAVIGATION:
                self.navigation = 0
                print ''
                print 'Navigation update'
                print 'Heading: ', self.heading
                # print 'Walk: ', str(walk_dir)
                # print ''

                if self.node_dir[0] == 1:
                    print 'Going node', self.node_dir[1]
                    self.audio.queue_sound(self.node_dir[1])
                # turn feedback
                if abs(turn_dir[1]) >= MIN_TURN_ANGLE:
                    if turn_dir[0] == 0:
                        print 'Turn Left'
                        print ''
                        # self.sound_turndir = 0
                        self.audio.queue_sound('left')
                    else:
                        print 'Turn Right'
                        print ''
                        # self.sound_turndir = 1
                        self.audio.queue_sound('right')
                else:
                    print 'Go'
                    print ''
                    # self.sound_turndir = 2
                    self.audio.queue_sound('go')
            else:
                self.navigation += 1

            # TODO: WIFI

        print 'Reached destination'
        self.audio.queue_sound('trapped', 'trapped')

        while (destination is not 0):
            # print 'done done done'
            self.audio.sound_dequeue()
            pass

    # debugging functions
    def get_map(self):
        coord = []
        self.map_x = []
        self.map_y = []
        url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?' + 'Building=' + self.building_start + '&Level=' + self.level_start

        try:
            data = json.loads(requests.get(url).text)
            info = data['info']
            if (info != None):
                local_map = data['map']
                for node in local_map:
                    self.map_x.append(int(node['x']))
                    self.map_y.append(int(node['y']))
        except:
            print  url
            print 'Failed to fetch map.'
            pass

    def test_position(self):
         self.position[0] = int(raw_input("Enter position x "))
         self.position[1] = int(raw_input("Enter position y "))
         #self.heading = float(raw_input("Enter heading "))
#run this
Main().main()
