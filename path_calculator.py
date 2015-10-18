import math
import Queue

from priority_dictionary import PriorityDictionary
from collections import defaultdict

class PathCalculator:
    """
    pathCalculator calculates the shortest path using Dijkstra's algorithm
    path is returned in the form of an array of (int)nodeId
    """
    def __init__(self):
        self.mapList = {}
        self.path = []
        self.edges = defaultdict(int)
        self.start = 0
        self.end = 0
    
    def dijkstra_relaxation(self):
            #for all the links from the node, relax neighbours
        D = {}	# dictionary of final distances
        P = {}	# dictionary of predecessors
        Q = PriorityDictionary()   # est.dist. of non-final vert.
        Q[self.start] = 0

        try:
            for v in Q:
                D[v] = Q[v]
                if v == self.end: break
                #START NODE ERROR
                #START AND END NODE ERROR
                links = self.mapList[v]["links"]
                #
                for w in links:
                    vwLength = D[v] + self.edges[(v,w)]
                    if w in D:
                        if vwLength < D[w]:
                            raise ValueError
                    elif w not in Q or vwLength < Q[w]:
                        Q[w] = vwLength
                        P[w] = v
            check_start_node = 0
        except:
            check_start_node = 1
            pass
        return (D, P, check_start_node)
    
    #Find a single shortest path from the given start vertex
	#to the given end vertex.
	#The input has the same conventions as Dijkstra().
	#The output is a list of the vertices in order along
    #the shortest path
    def shortest_path(self):
        start = self.start
        end = self.end
        D, P, check_start_node = self.dijkstra_relaxation()
        Path = []

        if(check_start_node == 0):
            try:
                while 1:
                    Path.append(end)
                    if end == start: break
                    #END NODE ERROR
                    end = P[end]
                    #
                Path.reverse()
                check_end_node = 0
            except:
                check_end_node = 1
                pass
        else:
            check_end_node = 1 #if start node is invalid, end node will be invalid
        return (Path, check_start_node, check_end_node)

    #given mapList and start and end nodeIds
    #calculates shortest path and returns it
    def calculate_path(self, mapList, edges, start, end):
        self.mapList = mapList
        self.start = int(start)
        self.end = int(end)
        self.edges = edges
        self.path, check_start_node, check_end_node = self.shortest_path()
        return (self.path, check_start_node, check_end_node)
    
    def get_path(self):
        return self.path
    


    