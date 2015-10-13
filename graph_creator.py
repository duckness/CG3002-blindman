import math

from collections import defaultdict
   
class GraphCreator:
    """
    #TODO: implement wifi and info processing
    graphCreator takes in raw data from mapFetcher and
    processes the raw data.
    From map, it creates a list of nodes, mapList, indexed by nodeId(int).
    mapList:  (int)nodeId : {"nodeId"(int), "nodeName"(str), "links"([int, int]), "x"(int), "y"(int)}
    """
    def __init__(self):
        #list of nodes by id
        self.maplist = {}
        self.edges = defaultdict(int)
        self.edgelist = []
    
    #create mapList by nodeId
    #mapList:  (int)nodeId : {"nodeId"(int), "nodeName"(str), "links"([int, int]), "x"(int), "y"(int)}
    #this is to ensure that stripping/converting str to int only happens once, at the start
    def create_maplist(self, map):
        for i in xrange (0, len(map)):
            point = map[i]
            nodeId = int(point["nodeId"])
            self.maplist[nodeId] = {}
            self.maplist[nodeId]["nodeId"] = nodeId
            links = []
            linkstr = point["linkTo"].split(',')
            for j in xrange(0, len(linkstr)):
                links.append(int(linkstr[j].strip()))
            self.maplist[nodeId]["links"] = links
            self.maplist[nodeId]["nodeName"] = point["nodeName"]
            self.maplist[nodeId]["x"] = int(point["x"])
            self.maplist[nodeId]["y"] = int(point["y"])
        return self.maplist

    def create_edges(self):
        for i in self.maplist:
            links = self.maplist[i]["links"]
            for j in links:
                self.edgelist.append((i, j))
        
        for k in self.edgelist:
            x1 = self.maplist[k[0]]["x"]
            y1 = self.maplist[k[0]]["y"]
            x2 = self.maplist[k[1]]["x"]
            y2 = self.maplist[k[1]]["y"]
            self.edges[k] = self.calculate_distance(x1,y1,x2,y2)
        return self.edges

    def get_edges(self):
        return self.edges

    def get_maplist(self):
        return self.maplist
    
    #internal method to calculate distance between 2 points
    def calculate_distance(self, x1, y1, x2, y2):
        distance = math.hypot(x2-x1, y2-y1)
        return distance