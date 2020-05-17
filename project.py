from dwave_qbsolv import QBSolv

#                                                 original routes                     2 alternate routes
#  _ _ _ _    (road segment IDs) _ 0 1 2 3        1st car = [0, 5, 14, 19, 20, 21]    [0, 1, 2, 3, 8, 17], [4, 9, 10, 11, 16, 21]
# |_|_|_|_|   |4 5 6 7 8, _ 9 10 11 12            2nd car = [13, 18, 19]              [9, 10, 15], [9, 14, 19]
# |_|_|_|_|   |13 14 15 16 17, _ 18 19 20 21      3rd car = [6, 15, 20, 21]           [2, 3, 8, 17], [2, 7, 16, 21]

largestSegmentID = 21
numOfAlternateRoutes = 3

firstCarRoutes = [[0, 5, 14, 19, 20, 21], [0, 1, 2, 3, 8, 17], [4, 9, 10, 11, 16, 21]]
secondCarRoutes = [[13, 18, 19], [9, 10, 15], [9, 14, 19]]
thirdCarRoutes = [[6, 15, 20, 21], [2, 3, 8, 17], [2, 7, 16, 21]]

carRoutes = [firstCarRoutes, secondCarRoutes, thirdCarRoutes]


def getIntersections(route1, route2):
    intersections = []
    for i in range(0, len(route1)):
        if (route1[i] in route2):
            intersections.append(route1[i])
    return intersections

def getUniqueArr(arr):
    ansArr = []
    for i in range(0, len(arr)):
        if(arr[i] not in ansArr):
            ansArr.append(arr[i])
    return ansArr

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
        print(Q[(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j)])
        Q.update({(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j): (Q[(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j)] - lam)})
        print(Q[(i*numOfAlternateRoutes+j, i*numOfAlternateRoutes+j)])


# don't use the one below, there are small mistakes in the biases
# Q = {(0, 0): -6, (1, 1): -5, (2, 2): -6, (3, 3): -11, (4, 4): -9, (5, 5): -9, (6, 6): -8, (7, 7): -8, (8, 8): -8, (0, 1): 24, (0, 2): 24, (1, 2): 24, (3, 4): 24, (3, 5): 24, (4, 5): 24, (6, 7): 24, (6, 8): 24, (7, 8): 24, (0, 3): 2, (0, 5): 4, (0, 6): 4, (0, 8): 2, (1, 7): 8, (1, 8): 2, (2, 4): 4, (2, 5): 2, (2, 6): 2, (2, 8): 4, (4, 6): 2}

response = QBSolv().sample_qubo(Q)
print("samples=" + str(list(response.samples())))
print("energies=" + str(list(response.data_vectors['energy'])))
