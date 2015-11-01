# required imports
import math
from serial_processor import SerialProcessor
from navigator import Navigator
from obstacle import ObstacleCues
from user_input import UserInput
from audio import Audio

# debugging imports
import matplotlib.pyplot as plt
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
MAX_CALIBRATE       = 300
MAX_NAVIGATION      = 50
MIN_TURN_ANGLE      = 40
MAX_SOUND           = 120
SOUND_AT_NODE       = 3
SOUND_GOING_TO      = 10
# multiplier
MULTIPLIER_LIMIT    = 1.000001
MULTIPLIER_G        = 981 # cm
MULTIPLIER_DISTANCE = 1.75
MULTIPLIER_MAP      = 1.8
MULTIPLIER_HEADING  = 22.5
# user input
MAP_COM1            = '1'
MAP_COM2            = '2'

class Main:

    # initialize class
    def __init__(self):
        # modules
        self.processor  = SerialProcessor()
        self.navigator  = Navigator()
        self.obstacle   = ObstacleCues()
        self.user_input = User_Input()
        self.audio      = Audio()
        # map
        self.north_at   = 0
        self.building   = ''
        self.level      = ''
        self.start      = ''
        self.end        = ''
        self.position   = [0,0]
        self.x          = []
        self.y          = []
        # hardware
        self.dt         = 0
        self.acc        = [0,0,0]
        self.gyro       = [0,0,0]
        self.magno      = [0,0,0]
        self.heading    = 999
        self.pressure   = 0
        self.altitude   = 0
        self.temp       = 0
        self.sensors    = [[0,0],[0,0],[0,0],[0,0]]
        # calibration
        self.calibrate  = 0
        self.limit      = 0
        # calculations
        self.r          = 0
        self.distance   = 0
        self.heading_r  = 999
        # navigation
        self.navigation = 0
        #sound delay
        self.sound = 0
        self.sound_turndir = 2
        self.at_node_count = SOUND_AT_NODE
        self.going_to_node_count = SOUND_GOING_TO
        # debugging
        self.log        = None
        self.map_x      = []
        self.map_y      = []
        self.axis       = None
        self.line       = None

    # setup
    def setup(self):
        # input map info / all must be 0
        check_map, check_start, check_end = -1, -1, -1
        while (check_map!=0 or check_start!=0 or check_end!=0):
            self.get_map_input()
            check_map, check_start, check_end = self.naviagtor.calculate_path(self.building, self.level, self.start, self.end)

        # setup map
        self.north_at = self.navigator.get_northAt()
        self.position = self.navigator.get_position()
        self.x.append(self.position[0])
        self.y.append(self.position[1])

        # ready signal
        print 'System Ready.'

        # debugging
        self.log = open(sys.path[0] + "/Serial"+str(time())+".txt", 'w')
        self.get_map()
        plt.plot(self.map_x, self.map_y, 'bo')
        plt.ion()
        self.axis = plt.gca()
        self.line, = self.axis.plot(self.x, self.y, 'ro-')


    # get map input
    def get_map_input(self):
        print 'Input map information'
        self.audio.play_sound('trapped')

        # parsing of user input
        # 0: building / 1: level / 2: start / 3: end
        # expected behavior:
        #   keypress get sent when '#' is pressed. set to corresponding
        #   variable. increment to next variable. if blank is sent, ignore
        #   but keep the variable index.
        input_id = 0
        keypress = ''
        while input_id < 4:
            keypress = self.user_input.get_input()
            if keypress == '':
                continue

            if input_id == 0:
                self.building = keypress
                # defaults
                if self.building == MAP_COM1:
                    self.building = 'COM1'
                elif self.building == MAP_COM2:
                    self.building = 'COM2'
            elif input_id == 1:
                self.level = keypress
            elif input_id == 2:
                self.start = int(keypress)
            elif input_id == 3:
                self.end = int(keypress)
            else:
                input_id = -1

            input_id += 1

        print 'User Input: ',
        print self.building, self.level, str(self.start), str(self.end)

    # get serial data
    def get_mega_data(self):
        # get serial information in array format
        raw_data = self.processor.read_from_mega()

        if self.processor.verify_data(raw_data) == True:
            data_id = raw_data[0]
            raw_values = raw_data[1].split('/')

            # data processing
            parse_status = False
            if data_id == ID_IMU:
                parse_status = process_imu(raw_values)
            elif data_id == ID_HEADING:
                parse_status = process_heading(raw_values)
            else:
                parse_status = process_sensor(data_id, raw_values)

            # debugging
            self.log.write(raw_data[0] + ', ' + raw_data[1] + ', ' + raw_data[2] + '\n')
            self.log.flush

        return parse_status

    # imu processing
    def process_imu(self, raw_values):
        # ensure data integrity
        if len(raw_values) != 13:
            return False

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
        if self.calibrate < MAX_CALIBRATION:
            self.limit = max(self.limit, self.r)
        elif self.calibrate == MAX_CALIBRATION:
            self.limit *= MULTIPLIER_LIMIT;
        else:
            if self.r > self.limit:
                self.distance += self.r * MULTIPLIER_G * self.dt * self.dt * MULTIPLIER_DISTANCE * MULTIPLIER_MAP

        return True

    # heading processing
    def process_heading(self, raw_values):
        # ensure data integrity
        if len(raw_values) != 1:
            return False

        # parsing of raw_values
        try:
            self.heading = float(raw_values[0])
        except ValueError:
            return False

        if self.calibrate <= MAX_CALIBRATION:
            return True

        # calculations
        sections = round(self.heading/MULTIPLIER_HEADING, 0)
        self.heading_r = sections * MULTIPLIER_HEADING

        # position
        pos_offset = self.process_position()
        self.x.append(self.x[-1] + pos_offset[0])
        self.y.append(self.y[-1] + pos_offset[1])
        self.position[0] = self.x[-1]
        self.position[1] = self.y[-1]

        # prepare for new set of heading information
        self.distance = 0

        # debugging
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        self.axis.relim()
        plt.draw()
        plt.pause(0.0000001)

        return True

    # sensors processing
    def process_sensor(self, data_id, raw_values):
        # ensure data integrity
        if len(raw_values) != 2:
            return False

        # parsing of raw_values
        try:
            index = int(data_id)/10 - 1
            self.sensors[index][0] = int(raw_values[0])
            self.sensors[index][1] = int(raw_values[1])

            if (index == 1 and self.calibrate < MAX_CALIBRATION):
                self.obstacle.initial_calibration(self.sensors[index])

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
        y_degree = self.heading_r + offset_y_angle
        if y_degree == 360:
            y_degree = 0
        elif yDeg < 0:
            y_degree += 360

        # calculate position from heading
        y_degree_rad = math.radians(y_degree)
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
            if self.calibrate < MAX_CALIBRATION:
                if self.calibrate == 0:
                    print 'Start Calibration'

                if self.calibrate == MAX_CALIBRATION:
                    print 'End Calibration'
                    print 'Limit: ', self.limit

                self.calibrate += 1
                continue

            # obstacle
            obstacle_detected = self.obstacle.detect_obstacles(self.sensors)
            if obstacle_detected == self.obstacle.OBSTACLE_STEP_DOWN:
                print 'Beware step down'
                self.audio.play_sound('step_below')
            elif obstacle_detected == self.obstacle.OBSTACLE_STEP_UP:
                print 'Beware step up'
                self.audio.play_sound('near_knee')
            else:
                print "stop"
                self.audio.play_sound('stop')

            #play sound
            if self.sound >= MAX_SOUND:
                self.sound = 0
                if self.sound_turndir == 0:
                    self.audio.play_sound('left')
                elif self.sound_turndir == 1:
                    self.audio.play_sound('right')
                else:
                    self.audio.play_sound('go')
            else:
                self.sound += 1

            # navigation
            if self.navigation >= MAX_NAVIGATION:
                self.navigation = 0
                print 'Navigation update'

                node_dir, turn_dir, walk_dir, destination = self.navigator.get_directions(self.position[0], self.position[1], self.heading_r)

                print 'Heading: ', self.heading_r
                print 'Walk: ', str(walk_dir)

                if destination == 1:
                    break
                else:
                    # node feedback
                    if node_dir[0] == 0:
                        print 'Reached node'
                        self.at_node_count += 1
                        self.going_to_node_count = SOUND_GOING_TO
                        if(self.at_node_count >= SOUND_AT_NODE):
                            self.audio.play_number(node_dir[1], 'node')
                            self.at_node_count = 0
                    elif node_dir[0] == 1:
                        print 'Going node'
                        self.going_to_node_count += 1
                        self.at_node_count = SOUND_AT_NODE
                        if(self.going_to_node_count >= SOUND_GOING_TO):
                            self.audio.play_number(node_dir[1])
                            self.going_to_node_count = 0
                    # turn feedback
                    if abs(turn_dir[1]) >= MIN_TURN_ANGLE:
                        if turn_dir[0] == 0:
                            print 'Turn Left'
                            self.sound_turndir = 0
                        else:
                            print 'Turn Right'
                            self.sound_turndir = 1
                    else:
                        print 'Go'
                        self.sound_turndir = 2
            else:
                self.navigation += 1

            # TODO: WIFI

        print 'Reached destination'
        self.audio.play_sound('stop')

    # debugging functions
    def get_map(self):
        coord = []
        url = 'http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?' + 'Building=' + self.building + '&Level=' + self.level

        try:
            info = json.loads(requests.get(url).text)['info']
            if (info != None):
                local_map = data['map']
                for node in local_map:
                    self.map_x.append(int(node['x']))
                    self.map_y.append(int(node['y']))
        except:
            print 'Failed to fetch map.'
            pass
