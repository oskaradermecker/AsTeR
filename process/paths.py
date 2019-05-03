# Author:  DINDIN Meryll
# Date:    02 May 2019
# Project: AsTeR

class ShortestPath:

    def __init__(self, graph):

        self.G = graph

    def dijkstra(self, origin, goal):

        inf = float('inf')
        D = {origin: 0}
        Q = PQDict(D)
        P = {}
        U = set(self.G.keys())

        while U:

            (v, d) = Q.popitem()
            D[v] = d
            U.remove(v)
            if v == goal: break

            for w in self.G[v]:
                if w in U:
                    d = D[v] + self.G[v][w]
                    if d < Q.get(w, np.inf):
                        Q[w] = d
                        P[w] = v

        v = goal
        path = [v]

        while v != origin:
            v = P[v]
            path.append(v) 

        path.reverse()

        return path

