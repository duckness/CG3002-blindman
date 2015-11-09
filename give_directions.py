from map_fetcher import MapFetcher
from path_calculator import PathCalculator

import math
HEADING_CONSTANT = 22.5
DISTANCE_CONSTANT = 0.12

class GiveDirections:

    def __init__(self):
        self.mapfetcher = MapFetcher()
        self.pathcalculator = PathCalculator()
        self.building = ""
        self.level = ""
        self.maplist = ""
        self.edges = ""
        self.path = ""
        self.northAt = ""
        self.prevNode = ""
        self.nextNode = ""
        self.lastNode = 0
        self.prevRadius = 200

    def fetch_map(self, building, level, start, end):
        self.building = building
        self.level = level
        self.maplist, self.edges, check_map = self.mapfetcher.fetch_map(building, level)
        if(check_map == 0):
            self.northAt = float(self.mapfetcher.get_info()['northAt'])
            self.path, check_start_node, check_end_node = self.pathcalculator.calculate_path(self.maplist, self.edges, start, end)
            if(check_start_node == 0 and check_end_node == 0):
                if (start == end):
                    self.prevNode = self.path[0]
                    self.nextNode = self.path[0]
                else:
                    self.prevNode = self.path[0]
                    self.nextNode = self.path[1]
        else: #if map is invalid, set the nodes to be invalid too
            check_start_node = 1
            check_end_node = 1
        return (check_map, check_start_node, check_end_node)

    def walking_direction(self, point1, point2):
        if point1[0] < point2[0]:
            if point1[1] < point2[1]:
                return math.degrees(math.atan2((point2[0] - point1[0]),(point2[1] - point1[1])))
            elif point1[1] > point2[1]:
                return 180 - math.degrees(math.atan2 ((point2[0] - point1[0]), (point1[1] - point2[1])))
            else:
                return 90
        elif point1[0] > point2[0]:
            if point1[1] < point2[1]:
                return 360 - math.degrees(math.atan2((point1[0] - point2[0]),(point2[1] - point1[1])))
            elif point1[1] > point2 [1] :
                return 180 + math.degrees(math.atan2((point1[0] - point2[0]),(point1[1] - point2 [1])))
            else:
                return 270
        else:
            if point1[1] < point2[1]:
                return 360
            else:
                return 180

    def turning_angle(self, heading, newheading):
        ang = newheading - heading
        if (ang > 180):
            ang -= 360
        elif (ang < -180):
            ang += 360
        return ang

    def turning_direction(self, angle):
        if (angle == 0):
            direction = "Go Straight"
            direction = (2, 0)
        elif (angle < 0):
            direction = "Turn Left by " + str(round(-(angle), 2)) + " degrees"
            direction = (0, -angle)
        else:
            direction = "Turn Right by " + str(round(angle, 2)) + " degrees"
            direction = (1, angle)
        return direction

    def distance_from_node(self, x, y, node):
        return math.hypot(x-self.maplist[node]['x'], y-self.maplist[node]['y'])

    def convert_compass_angle(self, cangle):
        ang = cangle + self.northAt
        if(ang > 360):
            ang -= 360
        return ang

    def turn_direction_to_node(self, x, y, heading, target_node):
        curr = [x, y]
        nxt = [self.maplist[target_node]['x'], self.maplist[target_node]['y']] #get coordinates of target node
        currheading = self.convert_compass_angle(heading) #get map angles
        walk_angle = self.walking_direction(curr, nxt) #get angle from one point to another
        angle = self.turning_angle(currheading, walk_angle) #adjust the angle with the map angles
        turning_dir = self.turning_direction(angle)
        return turning_dir

    def get_next_node(self):
        for i in range(len(self.path)):
            if (self.nextNode == self.path[i]):
                if (i != len(self.path)-1):
                    return self.path[i+1]
                else:
                    return -1 #reached destination
        return None #error

    def giving_exact_direction(self, x, y, heading, targetNode):
        destination = 0
        targetNodeDist = self.distance_from_node(x, y, targetNode)

        if(targetNode == self.path[len(self.path)-1]):
            self.lastNode = 1; #going to last node in the path

        #if the exact distance is reached
        if (targetNodeDist <= 0):
            for _i in range(0,len(self.path)):
                i = self.path[_i] #i = node of path at index _i

                if (targetNode == i):
                    if (_i == len(self.path)-1): #if it is at the end of path array
                        node_direction = "Reached exact destination"
                        node_direction = (2, 0, 0)
                        destination = 1
                    # else:
                    #     node_direction =  "At node " + str(targetNode) + " exactly"
                    #     node_direction = (1, targetNode)
                    #     targetNode = self.path[_i+1]
                    #     targetNodeDist = self.distance_from_node(x,y,targetNode)
                    #
                    #     self.prevNode = self.nextNode
                    #     self.nextNode = self.get_next_node()
                    #     break
        else:
            node_direction = "" #to allow the addition of rough/vauge directions

        turn_direction = self.turn_direction_to_node(x, y, heading, targetNode)
        walk_direction = "Walk " + str(round(targetNodeDist, 2)) + " centimeters"
        walk_direction = (round(targetNodeDist, 2))
        return (node_direction, turn_direction, walk_direction, destination)

    def giving_vauge_direction(self, dist_from_prev_node, dist_between_nodes, heading):
        destination = 0
        node_direction = (3,0,0)

        #if distance from current to first node < 12% of the distance between both nodes
        if((dist_from_prev_node < (DISTANCE_CONSTANT*dist_between_nodes))):
            bigger = max(self.prevRadius, DISTANCE_CONSTANT*dist_between_nodes, 88)
            if(bigger > dist_from_prev_node):
                node_direction = "At node " + str(self.prevNode)
                node_direction = (0, self.prevNode, self.check_heading(heading))

        #if distance from current to first node > 88% of the distance between both nodes
        elif((dist_from_prev_node > ((1-DISTANCE_CONSTANT)*dist_between_nodes))):
            node_direction = "At node " + str(self.nextNode)
            node_direction = (0, self.nextNode, 0)

            #if going to last node on the path
            if(self.lastNode == 1):
                node_direction = "Reached destination"
                node_direction = (2, 0, 0)
                destination = 1

            self.prevRadius = 0.12*dist_between_nodes
            self.prevNode = self.nextNode
            self.nextNode = self.get_next_node()

        #if distance from current to first node is >12% but <88% of the distance between both nodes
        else:
            node_direction = "Going to node " + str(self.nextNode)
            node_direction = (1, self.nextNode, 0)

        return (node_direction, destination)

    def locate_position(self, x, y, heading):
        dist_from_prev_node = self.distance_from_node(x, y, self.prevNode)
        if (self.prevNode == self.nextNode):
            node_direction = "Reached destination"
            node_direction = (2, 0, 0)
            turn_direction = (3, 0)
            walk_direction = 0
            destination = 1
        else:
            prevNode_x = self.maplist[self.prevNode]['x']
            prevNode_y = self.maplist[self.prevNode]['y']
            dist_between_nodes = self.distance_from_node(prevNode_x, prevNode_y, self.nextNode)

            #get exact directions
            node_direction, turn_direction, walk_direction, destination = self.giving_exact_direction(x, y, heading, self.nextNode)
            if (node_direction == ""):
                #get vauge directions
                node_direction, destination = self.giving_vauge_direction(dist_from_prev_node, dist_between_nodes, heading)

        #testing code below
        #if(self.nextNode != -1):
            #print "Prev node: " +str(self.prevNode) + ", Info: " + str(self.maplist[self.prevNode])
            #print "Next node: " + str(self.nextNode) + ", Info: " + str(self.maplist[self.nextNode])

        #print "-"

        return (node_direction, turn_direction, walk_direction, destination)

    def first_node_coordinates(self):
        firstNode = self.path[0]
        firstNode_x = self.maplist[firstNode]['x']
        firstNode_y = self.maplist[firstNode]['y']
        return [firstNode_x, firstNode_y]

    #takes in x_coor y_coor macAddr and distance to the accesspoint, checks weather if within the specified distance
    def nearby_wifi(self, x, y, macAddr, range):
        for accesspoint in self.mapfetcher.wifi:
            if (accesspoint['nodeName'] == macAddr):
                print accesspoint
                dist_calculated = math.hypot(x - float(accesspoint['x']),y - float(accesspoint['y']))
                print dist_calculated
                if (dist_calculated <= range):
                    return True
        return False

    def check_heading(self, heading):
        ang = self.heading_from_prev_node()
        multiplier = round(ang/HEADING_CONSTANT, 0)
        ang = multiplier * HEADING_CONSTANT

        multiplier = round(heading/HEADING_CONSTANT, 0)
        heading_ang = multiplier * HEADING_CONSTANT

        if (ang == heading_ang):
            return 1
        else:
            return 0

        # ang =  360 - self.northAt + map_angle
        # if(ang >= self.northAt):
        #     ang -= self.northAt

    def heading_from_prev_node(self):
        x1 = self.maplist[self.prevNode]['x']
        y1 = self.maplist[self.prevNode]['y']
        x2 = self.maplist[self.nextNode]['x']
        y2 = self.maplist[self.nextNode]['y']
        prev_arr = [x1, y1]
        next_arr = [x2, y2]

        map_angle = self.walking_direction(prev_arr, next_arr)
        ang = map_angle - self.northAt
        if(ang < 0):
            ang += 360

        return ang

    def get_nodes_position(self):
        x1 = self.maplist[self.prevNode]['x']
        y1 = self.maplist[self.prevNode]['y']
        x2 = self.maplist[self.nextNode]['x']
        y2 = self.maplist[self.nextNode]['y']
        return (x1, y1, x2, y2)

