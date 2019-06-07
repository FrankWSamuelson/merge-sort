from DylUtils import *

class Comparator:
    def __init__(self, objects: list = None, level: int = 3):
        self.clearHistory()
        self.level: int = level
        self.compHistory = list()
        self.dupHistory = 0
        self.optHistory = 0
        self.counts = dict()
        self.minSeps = dict()
        if objects != None:
            self.genLookup(objects)
        self.last: tuple = None
    def __len__(self):
        return self.compHistory if type(self.compHistory) == int else len(self.compHistory)
    def __call__(self, a, b):
        return self.compare(a,b)
    def compare(self, a, b) -> bool:
        """returns a < b
        based on optimization level, will not optimize, store result, or do abc association"""
        try:
            if b in self.lookup[a].keys():
                # print("cache hit")
                return self.lookup[a][b]
            elif a in self.lookup[b].keys():
                # print("cache hit")
                return self.lookup[b][a]
            else:
                # print("cache miss", a, b)
                res:bool = a < b
                self.counts[a] += 1
                self.counts[b] += 1

                #count minimum separations
                for i,(compA, compB) in enumerate(reversed(self.compHistory)):
                    if i < self.minSeps[a] and (a == compA or a == compB):
                        self.minSeps[a] = i
                    if i < self.minSeps[b] and (b == compA or b == compB):
                        self.minSeps[b] = i
                self.compHistory.append([a,b])
                if self.last:
                    if a in self.last or b in self.last:
                        self.dupHistory += 1
                self.last = ((a, b))
                if self.level > 0:
                    self.lookup[a][b]:bool = res
                    self.lookup[b][a]:bool = not res

                if self.level > 1:
                    # print("optimizing")
                    # single optimization
                    for c in self.lookup[b].keys():
                        # for all c s.t. we know the relationship b/t b and c
                        if self.lookup[b][c] == res:# a < b < c or a > b > c
                            # print("optimized", a, c)
                            self.lookup[a][c]:bool = res  # a < c or a > c 
                            self.lookup[c][a]:bool = not res
                            self.optHistory += 1
                    for c in self.lookup[a].keys():
                        # for all c s.t. we know the relationship b/t b and c
                        if self.lookup[a][c] == (not res):# a < b < c or a > b > c
                            # print("optimized", b, c)
                            self.lookup[b][c]:bool = not res  # a < c or a > c 
                            self.lookup[c][b]:bool = res
                            self.optHistory += 1
                if self.level > 2:
                    # O(n!) optimization. Make sure to use a copy of objects
                    self.optHistory += Comparator.optimize(list(self.lookup.keys()), self.lookup, res, a, b)
                return res
        except AttributeError as e:
            raise LookupError("You need to generate the lookup first")
    def genLookup(self, objects: list):
        self.lookup:dict = dict()
        self.objects: list = objects
        for object in objects:
            self.lookup[object] = dict()
            self.counts[object] = 0
            self.minSeps[object] = 2*len(objects)
    
    def clearHistory(self):
        self.compHistory = list()

    @staticmethod
    def optimize(objects: list, lookup: dict, res: bool, a, b):
        if objects:
            nObjects: list = []
            for c in list(lookup[b]): 
                # for all c s.t. c is a neighbor of b
                if c in objects and lookup[b][c] == res and c != a and c not in lookup[a]: 
                    # s.t. a > b > c or a < b < c
                    nObjects.append(c)
                    # print("optimized", a, c)
                    lookup[a][c]:bool = res
                    lookup[c][a]:bool = not res
                    return 1 + Comparator.optimize(nObjects, lookup, res, b, c)
        return 0

if __name__ == "__main__":
    comp = Comparator([i for i in range(10)], 2)
    print(comp.compare(0, 1))
    print(comp.compare(1, 2))
    print(comp.compare(0, 2))
    print(comp.compare(2, 0))
    print(comp.compare(0, 3))
    print(comp.compare(2, 3))