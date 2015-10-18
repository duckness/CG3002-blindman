from map_fetcher import MapFetcher
from path_calculator import PathCalculator

import math

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

    def fetch_map(self, building, level, start, end):
        self.building = building
        self.level = level
        self.maplist, self.edges, checkmap = self.mapfetcher.fetch_map(building, level)
        if(checkmap == 0):
            self.northAt = float(self.mapfetcher.get_info()['northAt'])
            self.path = self.pathcalculator.calculate_path(self.maplist, self.edges, start, end)
            self.prevNode = self.path[0]
            self.nextNode = self.path[1]
        return checkmap

    def walking_direction(self, point1, point2):
        if point1[0] < point2[0]:
            if point1[1] < point2[1]:
                return math.degrees(math.atan2((point2[0] - point1[0]),(point2[1] - point2[0])))
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
            direction = (0, angle)
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
        #if the exact distance is reached
        if (targetNodeDist <= 0):
            for _i in range(0,len(self.path)):
                i = self.path[_i] #i = node of path at index _i

                if (targetNode == i):
                    if (_i == len(self.path)-1): #if it is at the end of path array
                        node_direction = "Reached exact destination"
                        node_direction = (2, 0)
                        destination = 1
                    else:
                        node_direction =  "At node " + str(targetNode) + " exactly"
                        node_direction = (1, targetNode)
                        targetNode = self.path[_i+1]
                        targetNodeDist = self.distance_from_node(x,y,targetNode)

                        self.prevNode = self.nextNode
                        self.nextNode = self.get_next_node()
                        break
        else:
            node_direction = "" #to allow the addition of rough/vauge directions

        turn_direction = self.turn_direction_to_node(x, y, heading, targetNode)
        walk_direction = "Walk " + str(round(targetNodeDist, 2)) + " centimeters"
        walk_direction = (round(targetNodeDist, 2))
        return (node_direction, turn_direction, walk_direction, destination)

    def giving_vauge_direction(self, dist_from_prev_node, dist_between_nodes):
        destination = 0
        #if distance from current to first node < 10% of the distance between both nodes
        if((dist_from_prev_node < (0.1*dist_between_nodes))):
            node_direction = "At node " + str(self.prevNode)
            node_direction = (1, self.prevNode)

        #if distance from current to first node > 90% of the distance between both nodes
        elif((dist_from_prev_node > (0.9*dist_between_nodes))):
            node_direction = "At node " + str(self.nextNode)
            node_direction = (1, self.nextNode)

            #if distance from current to first node >= distance between both nodes
            if(dist_from_prev_node >= dist_between_nodes):
                self.prevNode = self.nextNode
                self.nextNode = self.get_next_node()

                if(self.nextNode == -1):
                    node_direction = "Reached destination"
                    node_direction = (2, 0)
                    destination = 1
        #if distance from current to first node is >10% but <90% of the distance between both nodes
        else:
            node_direction = "Going to node " + str(self.nextNode)
            node_direction = (1, self.nextNode)

        return (node_direction, destination)

    def locate_position(self, x, y, heading):
        dist_from_prev_node = self.distance_from_node(x, y, self.prevNode)

        prevNode_x = self.maplist[self.prevNode]['x']
        prevNode_y = self.maplist[self.prevNode]['y']
        dist_between_nodes = self.distance_from_node(prevNode_x, prevNode_y, self.nextNode)

        #get exact directions
        node_direction, turn_direction, walk_direction, destination = self.giving_exact_direction(x, y, heading, self.nextNode)
        if (node_direction == ""):
            #get vauge directions
            node_direction, destination = self.giving_vauge_direction(dist_from_prev_node, dist_between_nodes)

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
            if (accesspoint['macAddr'] == macAddr):
                print accesspoint
                dist_calculated = math.hypot(x - float(accesspoint['x']),y - float(accesspoint['y']))
                print dist_calculated
                if (dist_calculated <= range):
                    return True
        return False