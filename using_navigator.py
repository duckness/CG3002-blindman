from navigator import Navigator

class UsingNavigator:
    def __init__(self):
        self.navigator = Navigator()
        #testing for while loop variables below
        #self.x = ""
        #self.y = ""
        #self.heading = ""

    def setup(self):
        self.navigator.calculate_path("COM1", "2", "15", "1")
        northAt = self.navigator.get_northAt()
        #print "northAt: " + str(northAt)
        starting_position = self.navigator.get_position()
        print "Starting position: " + str(starting_position)
        print "-"

    def loop(self):
        #node direction, turn direction, walk direction, destination check will be returned by get_directions

#testing with customized coordinates and headings below
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 2000, 225)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 1787, 225)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(5603, 1787, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 1787, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 2436, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2883, 2436, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2152, 2436, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(0, 2436, -45)
        print node_dir + ", " + turn_dir + ", " + walk_dir


#testing for while loop below
        #self.x = 8000
        #self.y = 2000
        #self.heading = 50
        #destination_check = 0

        #while(destination_check != 1):
            #self.x += 500
            #self.y += 500
            #self.heading += 1
            #node_direction, turn_direction, walk_direction, destination_check = self.navigator.get_directions(self.x, self.y, self.heading)
            #print node_direction + ", " + turn_direction + ", " + walk_direction

navi = UsingNavigator()
navi.setup()
navi.loop()