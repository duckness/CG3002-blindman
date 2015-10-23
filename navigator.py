from give_directions import GiveDirections

class Navigator:
    def __init__(self):
        self.giveDir = GiveDirections()

    #setup map and path
    def calculate_path(self, building, level, start, end):
        #calculate_path = check_map, check_start_node, check_end_node (INT, INT, INT)
            #check_map: 0 = map is valid, 1 = map is invalid (no data in url), 2 = map is invalid (does not exist in storage)
            #check_start_node: 0 = start node is valid, 1 = start node is invalid
            #check_end_node: 0 = end node is valid, 1 = end node is invalid
        #note: if start node is invalid, end node will be invalid (need start node to calculate end node)
        return self.giveDir.fetch_map(building, level, start, end)

    #returns coordinates of the starting node
    #requires the shortest path to be calculated first
    def get_position(self):
        return self.giveDir.first_node_coordinates()

    #returns northAt of the map
    def get_northAt(self):
        return self.giveDir.northAt

    #returns directions to next node with current coordinates and heading
    def get_directions(self, x, y, heading):
        #directions is made up of (node_direction, turn_direction, walk_direction, destination) respectively
        #node_direction = (direction, node num, check_heading) (TUPLE)
            #(0, num) = At node num, (1, num) = Going to node num, (2, 0) = Reached destination, (3, 0) = Rubbish for start
            #(X, X, 0) = Don't lock, (X, X, 1) = Lock
        #turn_direction = (direction, degree) (TUPLE)
            #(0, degree) = Turn left, (1, degree) = Turn right, (2, degree) = Go straight, (3, 0) = Invalid (Start=End)
        #walk_direction = distance (FLOAT) (0 = Invalid (Start=End))
        #destination = check (INT)
        #1 = reached destination, 0 = have not reached destination
        return self.giveDir.locate_position(x, y, heading)

    def check_wifi(self, x, y, macAddr, range):
        return self.giveDir.nearby_wifi(self, x, y, macAddr, range)

    def heading_from_prev_node(self):
        return self.giveDir.heading_from_prev_node()

#testing codes below
    #def main(self):
        #self.calculate_path("COM1", "2", "15", "1") #setup
        #print self.get_directions(8000, 2000, 50)
        #print self.get_directions(5000, 2000, 60)

#navigator = Navigator()
#navigator.main()
