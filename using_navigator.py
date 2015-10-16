from navigator import Navigator

class UsingNavigator:
    def __init__(self):
        self.navigator = Navigator()
        self.x = ""
        self.y = ""
        self.heading = ""

    def setup(self):
        self.navigator.calculate_path("COM1", "2", "15", "1")
        northAt = self.navigator.get_northAt()

    def loop(self):
        self.x = 8000
        self.y = 2000
        self.heading = 50
        destination_check = 0

        while(destination_check != 1):
            self.x += 500
            self.y += 500
            self.heading += 1
            node_direction, turn_direction, walk_direction, destination_check = \
                self.navigator.get_directions(self.x, self.y, self.heading)
            print node_direction + ", " + turn_direction + ", " + walk_direction

navi = UsingNavigator()
navi.setup()
navi.loop()

