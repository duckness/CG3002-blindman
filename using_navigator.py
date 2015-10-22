from navigator import Navigator

class UsingNavigator:
    def __init__(self):
        self.navigator = Navigator()
        #testing for while loop variables below
        #self.x = ""
        #self.y = ""
        #self.heading = ""

    def setup_and_run(self):
        check_map, check_start_node, check_end_node = self.navigator.calculate_path("COM1", "2", "15", "1")
        if(check_map == 1): #if map is invalid
            print "Invalid map! No data in url"
        elif(check_map == 2): #if map is invalid
            print "Invalid map! Does not exist in storage"
        else: #if map is valid
            if(check_start_node == 1): #if start node is invalid (end node will also be invalid)
                print "Invalid nodes!"
            else: #if start node is valid
                if(check_end_node == 1): #if end node is invalid
                    print "Invalid end node!"
                else: #if end node is valid
                    if(check_start_node == 0 and check_end_node == 0): #if start node and end node are valid
                        print "Shortest path: " + str(self.navigator.giveDir.path)
                        northAt = self.navigator.get_northAt()
                        #print "northAt: " + str(northAt)
                        starting_position = self.navigator.get_position()
                        print "Starting position: " + str(starting_position)
                        print "-"
                        self.loop()

    #node and turn returns TUPLE (x, x), walk returns FLOAT, dest returns INT
    def print_output(self, node, turn, walk, dest):
        print node
        print turn
        print "Walk distance: " + str(walk)
        print "Destination Check: " + str(dest)
        print "-"

    def loop(self):
        #node direction, turn direction, walk direction, destination check will be returned by get_directions

#testing with customized coordinates and headings below
        #to print string: print node_dor + ", " + turn_dir + ", " + walk_dir

        #exact location testing with str (15 to 1)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 2000, 225)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 1787, 225)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(5603, 1787, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 1787, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 2436, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2883, 2436, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2152, 2436, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        # node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(0, 2436, -45)
        # self.print_output(node_dir, turn_dir, walk_dir, dest_check)

        #vauge location testing with output numbers
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 2000, 225)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(7065, 1787, 225)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(5623, 1787, -45)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 1787, -45)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(3776, 2436, -45)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2883, 2436, -45)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(2152, 2436, -45)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(0, 2436, 135)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(1000, 2436, 310)
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)
        node_dir, turn_dir, walk_dir, dest_check = self.navigator.get_directions(330, 2600, 45) #330-340
        self.print_output(node_dir, turn_dir, walk_dir, dest_check)

#testing for while loop below (for str)
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
navi.setup_and_run()