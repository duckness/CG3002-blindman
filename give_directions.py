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
        self.northAt = 0

    def walking_direction (self, point1, point2):

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

    def turn_angle(self, heading, newheading):
        ang = newheading - heading
        if (ang > 180):
            ang -= 360
        elif (ang < -180):
            ang += 360
        return ang

    def turn_direction(self, angle):
        if (angle == 180):
            return "Why..."
        elif (angle == 0):
            return "Go Straight"
        elif (angle < 0):
            return 'Turn Left %.2f' % -(angle) + ' degrees'
        return 'Turn Right %.2f' % angle + ' degrees'

    def turn_direction2(self, prv, cur, nxt): #deprecated
        cur_angle = self.walking_direction(prv,cur)
        nxt_angle = self.walking_direction(cur,nxt)
        ang = self.turn_angle(cur_angle, nxt_angle)
        if (ang == 180):
            return "Why..."
        elif (ang == 0):
            return "Go Straight"
        elif (ang > 0):
            return "Turn Right"
        return "Turn Left"

    def fetch_map(self, building, level):
        self.building = building
        self.level = level
        self.maplist, self.edges = self.mapfetcher.fetch_map(
                                    building, level)
        self.northAt = float(self.mapfetcher.get_info()['northAt'])

    def calculate_path(self, start, end):
        self.path = self.pathcalculator.calculate_path(
                    self.maplist, self.edges, start, end)
        #print self.maplist
        #print 'Go Straight' #recalibrate here
        for i in range(0,len(self.path)):
            if (i != 0 and i!=len(self.path) - 1): #not first and last node
                prev = [self.maplist[self.path[i-1]]['x'], self.maplist[self.path[i-1]]['y']]
                curr = [self.maplist[self.path[i]]['x'], self.maplist[self.path[i]]['y']]
                nxt = [self.maplist[self.path[i+1]]['x'], self.maplist[self.path[i+1]]['y']]
              #  print self.turn_direction2(prev,curr,nxt)

    #    print "----"

    def distance_from_node(self, x, y, node):
        return math.hypot(x-self.maplist[node]['x'], y-self.maplist[node]['y'])

    def current_node(self, node):
        print 'You are near node', node

    def giving_direction(self, x, y, heading, targetNode):
        def direction_to_node(self, curr_x, curr_y, heading, node_index):
            def convert_compass_angle(cangle):
                ang = cangle + self.northAt
                if (ang > 360):
                    ang -= 360
                #print 'ang = ' + str(ang)
                return ang
            cur = [curr_x,curr_y]
            nxt = [self.maplist[node_index]['x'], self.maplist[node_index]['y']]
            curheading = convert_compass_angle(heading) #adjust to map angles
            return self.turn_angle(curheading, self.walking_direction(cur, nxt))

        targetNodeDist = self.distance_from_node(x, y, targetNode)
        if (targetNodeDist <= 0):
            for _i in range(0,len(self.path)):
                i = self.path[_i] #i = node of path at index _i
                #print targetNode, self.maplist[i]
                if (targetNode == i):
                    if (_i == len(self.path)-1): #if it is at the end of path array
                        print 'You are at the destination'
                        return
                    print 'You are on node', targetNode
                    targetNode = self.path[_i+1]
                    targetNodeDist = self.distance_from_node(x,y,targetNode)
                    break
        print 'I am going to node ' + str(targetNode)
        print self.turn_direction(direction_to_node(self,x,y,heading,targetNode))
        print 'Walk %.1f' % (targetNodeDist) + ' centimeters'

# Takes in x_coor y_coor macAddr and distance to it, checks weather if within the specified distance
    def nearby_wifi(self, x, y, macAddr, dist):
        for accesspoint in self.mapfetcher.wifi:
            if (accesspoint['macAddr'] == macAddr):
                print accesspoint
                dist_calculated = math.hypot(x - float(accesspoint['x']),y - float(accesspoint['y']))
                print dist_calculated
                if (dist_calculated <= dist):
                    return True
        return False

    def main(self):
        bldg = raw_input("Please enter the Building name ")
        bldg = bldg.upper();
        lvl = raw_input("Please enter the level ")
        self.fetch_map(bldg,lvl)
        start = int(raw_input("Please enter start node "))
        end = int(raw_input("Please enter end node "))
        self.calculate_path(start,end)
        print "The shortest path is"
        print self.path
        x_coor = int(raw_input("Please enter the x coordinate "))
        y_coor = int(raw_input("Please entet the y coordinate "))
        heading = int(raw_input("Please enter the heading "))
        self.giving_direction(x_coor,y_coor,heading)



#Testing
#
giveD = GiveDirections()

#giveD.main()
giveD.fetch_map("COM1", "2")
giveD.calculate_path(20, 5)
print giveD.nearby_wifi(269,2199,'e8:ba:70:61:c9:60',200)
# print giveD.path
# #print giveD.maplist
# # print "\ntest1"
# giveD.giving_direction(8283,1056,0)
# # print "\ntest2"
# # giveD.giving_direction(3353,732,0)
# # print "\ntest3 "
# # giveD.giving_direction(7065,1787,0)
# # print "\ntest4"
# # giveD.giving_direction(7065,1543,0)
# # print "\ntest5 "
# # giveD.giving_direction(9460,2802,0)
#
# # print giveD.turn_direction([200,100],[400,300])
# # print giveD.turn_direction2([200,100],[400,100],[200,100])
# # print giveD.walking_direction([3330,1787],[3330,934])
# # print giveD.walking_direction([11571,691],[11815,406])