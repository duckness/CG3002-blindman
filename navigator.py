from map_fetcher import MapFetcher
from path_calculator import PathCalculator
from give_directions import GiveDirections

class Navigator:
    def __init__(self):
        self.mapfetcher = MapFetcher()
        self.pathcalculator = PathCalculator()
        self.building = ""
        self.level = ""
        self.giveDir = GiveDirections()
        self.lastBroadcast = -1
        self.prevNode = -1
        self.nextNode = -1 #nextNode = -1 means destination reached

    def get_next_node(self):
        for i in range(len(self.giveDir.path)):
            if (self.nextNode == self.giveDir.path[i]):
                if (i != len(self.giveDir.path)-1):
                    print self.giveDir.maplist[self.giveDir.path[i+1]]
                    return self.giveDir.path[i+1]
                else:
                    return -1 #reached destination
        return None #error

    #returns coordinates of the starting node
    #requires the shortest path to be calculated first
    def get_position(self):
        firstNode = self.giveDir.path[0]
        firstNode_x = self.giveDir.maplist[firstNode]['x']
        firstNode_y = self.giveDir.maplist[firstNode]['y']
        #print firstNode_x
        #print firstNode_y
        return [firstNode_x, firstNode_y]

    def main_loop(self): #THIS ASSUMES NODES ARE AT LEAST 2-3m apart

        self.prevNode = self.giveDir.path[0] #starting node
        print self.giveDir.maplist[self.prevNode]
        self.nextNode = self.giveDir.path[1] #second node
        print self.giveDir.maplist[self.nextNode]

        while(self.nextNode != -1): #while destination is not reached
            heading = int(raw_input("Please enter the heading "))
            x_coor = int(raw_input("Please enter the x coordinate "))
            y_coor = int(raw_input("Please enter the y coordinate "))

            dist_from_prev_node = self.giveDir.distance_from_node(x_coor, y_coor, self.prevNode) #distance from current to first node

            prevNode_x = self.giveDir.maplist[self.prevNode]['x']
            prevNode_y = self.giveDir.maplist[self.prevNode]['y']
            dist_prev_to_next_node = self.giveDir.distance_from_node(prevNode_x, prevNode_y, self.nextNode) #distance from first to second node

            #if distance from current to first node < 10% of the distance away from first node
            if((dist_from_prev_node < (0.1*dist_prev_to_next_node))):
                self.giveDir.current_node(self.prevNode) #prints 'You are near node (num)' (first node)

            #if distance from current to first node > 10% of the distance away from first node
            if((dist_from_prev_node > (0.1*dist_prev_to_next_node))) :
                self.giveDir.giving_direction(x_coor, y_coor, heading, self.nextNode)

            #if distance from current to second node > 90% of the distance away from first node
            if((dist_from_prev_node > (0.9*dist_prev_to_next_node))):
                self.giveDir.current_node(self.nextNode) #prints 'You are near node (num)' (second node)
                self.prevNode = self.nextNode
                self.nextNode = self.get_next_node()
                print 'Prev node: ' + str(self.prevNode)
                print 'Next Node: ' + str(self.nextNode)
        print 'yay'

    def main(self):
        print "Please enter the Building name "
        self.bldg = 'com1'#self.userInput.get_input()
        print "Please enter the level "
        self.level = 2#self.userInput.get_input()
        self.giveDir.fetch_map(self.bldg,self.level)
        print "Please enter start node "
        start = 15#int(self.userInput.get_input())
        print "Please enter end node "
        end = 1#int(self.userInput.get_input())
        self.giveDir.calculate_path(start,end)
        print "The shortest path is"
        print self.giveDir.path
        self.main_loop()

#testing
#navigator = Navigator()
#navigator.main()
