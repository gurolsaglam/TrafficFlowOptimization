# DOCUMENTATION:
# You will need dwave_qbsolv and osmnx libraries to be able to use this program.
# Please use these lines below to install these packages:
# pip install dwave_qbsolv

# NOT REQUIRED
# pip install osmnx
# in order for osmnx to be downloaded, you may have to install rtree from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#rtree
# you may also have to install GDAL-API from:
# http://www.gisinternals.com/release.php
# this link is how to do it on windows: https://sandbox.idre.ucla.edu/sandbox/tutorials/installing-gdal-for-windows
# if even though GDAL is installed and Fiona still does not install, get the whl for Fiona from here:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona
#
# HOW TO USE
#
# On command window:
#    project.py example.txt


import sys
from dwave_qbsolv import QBSolv

class Node:
    
    def __init__(self, nodeID):
        self.__nodeID = nodeID
        self.__edges = []
    
    def getID(self):
        return self.__nodeID
    
    def getEdges(self):
        return self.__edges
    
    def hasEdge(self, edge):
        for i in range(0, len(self.__edges)):
            if (self.__edges[i].getID() == edge.getID()):
                return True
        return False
    
    def addEdge(self, edge):
        if (self.hasEdge(edge)):
            return False
        self.__edges.append(edge)
        edge.addNode(self)
        return True
    
    def equals(self, node):
        if (node.getID() is self.getID()):
            return True
        return False
    
    def getEdgeWithNode(self, node):
        for i in range(0, len(self.__edges)):
            if (self.__edges[i].getOtherNode(self).equals(node)):
                return self.__edges[i]
        return None


class Edge:
    
    def __init__(self, edgeID, nodeA = None, nodeB = None):
        self.__edgeID = edgeID
        self.__nodeA = nodeA
        self.__nodeB = nodeB
        if not (nodeA is None):
            nodeA.addEdge(self)
        if not (nodeB is None):
            nodeB.addEdge(self)
    
    def getOtherNode(self, node):
        if (self.__nodeA is node):
            return self.__nodeB
        elif (self.__nodeB is node):
            return self.__nodeA
        return None
    
    def getID(self):
        return self.__edgeID
    
    def getNodes(self):
        return (self.__nodeA, self.__nodeB)
    
    def addNode(self, node):
        if (self.__nodeA is None):
            self.__nodeA = node
            node.addEdge(self)
            return True
        elif (self.__nodeB is None and not self.__nodeA.getID() == node.getID()):
            self.__nodeB = node
            node.addEdge(self)
            return True
        return False
    
    def equals(self, edge):
        if (edge.getID() is self.getID()):
            return True
        return False

class Graph:
    
    def __init__(self):
        self.__nodes = []
        self.__edges = []
    
    def addNode(self, node):
        self.__nodes.append(node)
    
    def addNodes(self, nodes):
        self.__nodes.extend(nodes)
    
    def addEdge(self, edge):
        self.__edges.append(edge)
    
    def addEdges(self, edges):
        self.__edges.extend(edges)
    
    def getNodes(self):
        return self.__nodes
    
    def getEdges(self):
        return self.__edges
    
    def getNodeWithID(self, nodeID):
        for i in range(0, len(self.__nodes)):
            if (self.__nodes[i].getID() is nodeID):
                return self.__nodes[i]
        return None
    
    def getEdgeWithID(self, edgeID):
        for i in range(0, len(self.__edges)):
            if (self.__edges[i].getID() is edgeID):
                return self.__edges[i]
        return None
    
    

def isRoadInRoute(road, route2):
    for i in range(0, len(route2)):
        if (road.equals(route2[i])):
            return True
    return False

def getIntersections(route1, route2):
    intersections = []
    for i in range(0, len(route1)):
        if (route1[i] in route2): #isRoadInRoute(route1[i], route2)):
            intersections.append(route1[i])
    return intersections

def getUniqueArr(arr):
    ansArr = []
    for i in range(0, len(arr)):
        if(arr[i] not in ansArr):
            ansArr.append(arr[i])
    return ansArr

def getQuboMatrix(carRoutes, numOfAlternateRoutes):
    #getting the Q (qubo matrix) from carRoutes array (list)
    Q = {}
    for i in range(0, len(carRoutes)*numOfAlternateRoutes): # number of cars * number of alternate routes
        for j in range(0, len(carRoutes)*numOfAlternateRoutes):
            Q.update({(i, j): 0})

    carRouteIntersections = [0] * len(carRoutes)
    for i in range(0, len(carRoutes)):
        for j in range(0, numOfAlternateRoutes):
            # get the number of total intersections and write to this array
            carIntersections = []
            for k in range(i+1, len(carRoutes)):
                for m in range(0, numOfAlternateRoutes):
                    # get intersections of the two routes (not the same car)
                    intersections = getIntersections(carRoutes[i][j], carRoutes[k][m])
                    # write to the upper triangle
                    Q.update({(i*numOfAlternateRoutes+j, k*numOfAlternateRoutes+m): len(intersections)*2})
                    # save to the total intersections for diagonals
                    carIntersections.extend(intersections)
            # write to the diagonals
            Q.update({(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j): len(carIntersections)})
            # keep the number of unique intersections for lambda
            carRouteIntersections[i] = carRouteIntersections[i] + len(getUniqueArr(carIntersections))

    lam = max(carRouteIntersections)
    for i in range(0, len(carRoutes)):
        for j in range(0, numOfAlternateRoutes):
            # write "2*lambda" to the upper small triangle of each vehicle
            for k in range(j+1, numOfAlternateRoutes):
                Q.update({(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+k): lam*2})
            # subtract lambda from the diagonals
            Q.update({(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j): (Q[(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j)] - lam)})
    return Q


# AN OLDER EXAMPLE
#                                                 original routes                     2 alternate routes
#  _ _ _ _    (road segment IDs) _ 0 1 2 3        1st car = [0, 5, 14, 19, 20, 21]    [0, 1, 2, 3, 8, 17], [4, 9, 10, 11, 16, 21]
# |_|_|_|_|   |4 5 6 7 8, _ 9 10 11 12            2nd car = [13, 18, 19]              [9, 10, 15], [9, 14, 19]
# |_|_|_|_|   |13 14 15 16 17, _ 18 19 20 21      3rd car = [6, 15, 20, 21]           [2, 3, 8, 17], [2, 7, 16, 21]
#
# largestSegmentID = 21
# numOfAlternateRoutes = 3

# firstCarRoutes = [[0, 5, 14, 19, 20, 21], [0, 1, 2, 3, 8, 17], [4, 9, 10, 11, 16, 21]]
# secondCarRoutes = [[13, 18, 19], [9, 10, 15], [9, 14, 19]]
# thirdCarRoutes = [[6, 15, 20, 21], [2, 3, 8, 17], [2, 7, 16, 21]]

# carRoutes = [firstCarRoutes, secondCarRoutes, thirdCarRoutes]



def main(argv):
    
    file = open(argv[1])
    lines = file.readlines()
    file.close()
    
    #delete any comments and empty lines
    for i in range(len(lines)-1, -1, -1):
        #delete the newline character at the end
        temp = lines[i].split("\n")
        lines[i] = temp[0]
        
        temp = lines[i].split(" #")
        lines[i] = temp[0]
        temp = lines[i].split("#")
        lines[i] = temp[0]
        
        if (lines[i] is ""):
            tmp = lines.pop(i)
    
    numOfNodes = int(lines[0])
    
    #initialize graph and nodes
    graph = Graph()
    for i in range(0, numOfNodes):
        node = Node(i)
        graph.addNode(node)
    
    #initialize edges
    nextLine = 1
    numOfEdges = 0
    for i in range(0, numOfNodes):
        nodeIDs = lines[nextLine+i].split(" ")
        for j in range(0, len(nodeIDs)):
            nodeA = graph.getNodeWithID(i)
            nodeB = graph.getNodeWithID(int(nodeIDs[j]))
            
            edge_existing = nodeA.getEdgeWithNode(nodeB)
            if not (edge_existing is None):
                continue
            edge_existing = nodeB.getEdgeWithNode(nodeA)
            if not (edge_existing is None):
                continue
            
            edge = Edge(numOfEdges, nodeA, nodeB)
            graph.addEdge(edge)
            numOfEdges = numOfEdges + 1
    
    #print the edges
    # edges = graph.getEdges()
    # for i in range(0, len(edges)):
        # print(str(edges[i].getID()) + "  A: " + str(edges[i].getNodes()[0].getID()) + "  B: " + str(edges[i].getNodes()[1].getID()))
    
    nextLine = nextLine + numOfNodes
    numOfCars = int(lines[nextLine])
    nextLine = nextLine + 1
    
    #get original car routes for each car
    carRoutes = []
    for i in range(0, numOfCars):
        carRoutes.append([])
    
    for i in range(0, numOfCars):
        nodeIDs = lines[nextLine+i].split("-")
        route = []
        for j in range(0, len(nodeIDs)-1):
            nodeA = graph.getNodeWithID(int(nodeIDs[j]))
            nodeB = graph.getNodeWithID(int(nodeIDs[j+1]))
            edge = nodeA.getEdgeWithNode(nodeB)
            route.append(edge)
        carRoutes[i].append(route)
    nextLine = nextLine + numOfCars
    
    #get the alternate routes
    numOfAlternateRoutes = 3
    for i in range(0, numOfCars*(numOfAlternateRoutes-1)):
        carNum = int(lines[nextLine+i].split(" ")[0])
        nodeIDs = (lines[nextLine+i].split(" ")[1]).split("-")
        route = []
        for j in range(0, len(nodeIDs)-1):
            nodeA = graph.getNodeWithID(int(nodeIDs[j]))
            nodeB = graph.getNodeWithID(int(nodeIDs[j+1]))
            edge = nodeA.getEdgeWithNode(nodeB)
            route.append(edge)
        carRoutes[carNum].append(route)
    

    Q = getQuboMatrix(carRoutes, numOfAlternateRoutes)
    
    response = QBSolv().sample_qubo(Q)
    result = list(response.samples())
    result = result[0]
    resultingEnergy = list(response.data_vectors['energy'])
    resultingEnergy = resultingEnergy[0]

    # print("samples=" + str(result))
    # print("energies=" + str(list(response.data_vectors['energy'])))

    print("roads taken:")
    for i in range(0, len(result)):
        if (result[i] == 1):
            print("car " + str((i//numOfAlternateRoutes)+1) + ": route " + str((i%numOfAlternateRoutes)+1))

    print("Resulting energy: " + str(resultingEnergy))


if __name__ == "__main__":
    main(sys.argv)