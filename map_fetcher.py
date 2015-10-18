import requests
import json
import urllib

from graph_creator import GraphCreator

class MapFetcher:
    """
    mapFetcher uses requests and json to fetch the map details from the internet
    given the building and level. 
    If incorrect building/level is given, #TODO: what to do?
    info, map and wifi are retrieved using getInfo, getMap, getWifi
    Data is returned in raw form.
    """
    URL_STANDARD = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?"

    def __init__(self):
        self._map = ""
        self.info = ""
        self.wifi = ""

        self.building = ""
        self.level = ""

        self.graphcreator = GraphCreator()
        self.maplist = ""
        self.edges = ""

    def fetch_map(self, building, level):
        self.building = str(building)
        self.level = str(level)

        url = MapFetcher.URL_STANDARD + "Building=" + self.building + "&Level=" + self.level
        count = 0
        check_map = 0 #map is valid

        while(self.info == "" and count < 10):
            try:
                REQUEST = requests.get(url) #load json from url
                #code jumps to except in offline mode
                data = json.loads(REQUEST.text) #json is stored in data (in json format)
                self.info = data['info'] #store url data into info

                if(self.info != None): #if there is data in the url
                    self._map = data['map'] #store map data into map
                    self.wifi = data['wifi'] #store wifi data into wifi

                    original_text = urllib.urlopen(url) #load data from url
                    original_data = original_text.read() #data from url is stored in original data (in original format)
                    original_text.close()

                    file_name = self.building + "-level" + self.level + ".json"
                    text = open(file_name, 'w') #opens file in write format
                    text.write(str(original_data)) #writes original data into stored file
                    text.close()

                else:
                    #there is no data in the url!
                    #print "Invalid map! No data in url"
                    check_map = 1
            except: #offline: REQUEST will throw an exception and get into this loop
                count += 1

                if(count == 10):
                    print "Failed to download map details. Using Static Local Copy..."

                    try:
                        file_name = self.building + "-level" + self.level + ".json"
                        text = open(file_name) #opens file in read format (default format)
                        data = json.load(text) #reads stored file and stores json in data (in json format)

                        self.info = data['info'] #store file data info into info
                        self._map = data['map'] #store file data map into map
                        self.wifi = data['wifi'] #srore file data wifi into wifi

                    except IOError:
                        #file does not exist!
                        #print "Invalid map! Does not exist in storage"
                        check_map = 2
                        pass
            pass
        self.maplist = self.graphcreator.create_maplist(self._map)
        self.edges = self.graphcreator.create_edges()
        return (self.maplist, self.edges, check_map)
    
    #possible: implement the creating of the mapList here instead of graphCreator
    def get_map(self):
        return (self.maplist, self.edges)
    
    def get_info(self):
        return self.info

    def get_wifi(self):
        return self.wifi

    def get_building(self):
        return self.building

    def get_level(self):
        return self.level