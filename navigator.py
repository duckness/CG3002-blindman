from give_directions import GiveDirections

class Navigator:
    def __init__(self):
        self.giveDir = GiveDirections()

    #setup map and path
    def calculate_path(self, building, level, start, end):
        self.giveDir.fetch_map(building, level, start, end)
        #in fetch_map, the shortest path is printed

    #returns coordinates of the starting node
    #requires the shortest path to be calculated first
    def get_position(self):
        return self.giveDir.first_node_coordinates()

    #returns northAt of the map
    def get_northAt(self):
        return self.giveDir.northAt

    #returns directions to next node with current coordinates and heading
    def get_directions(self, x, y, heading):
        return self.giveDir.locate_position(x, y, heading)

#testing codes below
    #def main(self):
        #self.calculate_path("COM1", "2", "15", "1") #setup
        #print self.get_directions(8000, 2000, 50)
        #print self.get_directions(5000, 2000, 60)

#navigator = Navigator()
#navigator.main()
