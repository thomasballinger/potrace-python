
import sys
import functools

#TODO separate conditions of eqality from this
def cyclic_in_order(a, b, c):
    """Returns True if points are in order on a circle, a <= b < c < a"""
    if a <= c:
        return a <= b and b < c
    else:
        return a <= b

class Cycle(list):
    """A cyclical list with wrap-around indexing for read only"""
    def __init__(self, vertex_list=None):
        if vertex_list:
            list.extend(self, vertex_list)
    def append():  raise NotImplementedError
    def extend():  raise NotImplementedError
    def insert():  raise NotImplementedError
    def pop():     raise NotImplementedError
    def remove():  raise NotImplementedError
    def reverse(): raise NotImplementedError
    def __setitem__(self, key):  raise NotImplementedError
    def __delitem__(self, key):  raise NotImplementedError
    def __setslice__(self, key): raise NotImplementedError
    def __delslice__(self, key): raise NotImplementedError

    def __getitem__(self, key):
        return list.__getitem__(self, key % len(self))
    def __getslice__(self, i, j):
        print 'i:', i, 'j:', j
        if j == sys.maxint: # j was missing in slice expression
            j = i + len(self)
        if 0 <= i <= j <= len(self):
            return list.__getslice__(self, i, j)
        else:
            mod_i = i % len(self)
            mod_j = i % len(self)
            if i >= j:
                return list.__getslice__(self, i, j)
            if mod_i < mod_j:
                return list.__getslice__(self, mod_i, mod_j)
            else:
                return list.__getslice__(self, mod_i, sys.maxint) + list.__getslice__(self, 0, mod_j)
    def cycrange(self, i, j):
        #TODO make __getslice__ use this
        print 'i:', i, 'j:', j
        if j == sys.maxint: # j was missing in slice expression
            j = i + len(self)
        if 0 <= i <= j <= len(self):
            return range(i, j)
        else:
            mod_i = i % len(self)
            mod_j = i % len(self)
            if i >= j:
                return range(i, j)
            if mod_i < mod_j:
                return range(mod_i, mod_j)
            else:
                return range(mod_i, len(self)) + range(0, mod_j)

def mod_index(func):
    @functools.wraps(func)
    def new_func(self, i, *args, **kwargs):
        i = i % len(self)
        return func(self, i, *args, **kwargs)
    return new_func

class memoize():
    """Doesn't check the first argument when memoizing"""
    def __init__(self, func):
        self.orig_func = func
        self.cache = {}
        self.__name__ = func.__name__
    #TODO can functools.wraps be used here?
    def __call__(self, method_self, *args, **kwargs):
        key = (args, str(**kwargs))
        try:
            return self.cache[key]
        except KeyError:
            print 'calculating value this first time for', key
            self.cache[key] = self.orig_func(method_self, *args, **kwargs)
            return self.cache[key]

class Path(Cycle):
    """A closed path of touching vertices"""

    @mod_index
    def next_corner(self, index):
        """The next corner (looking forward) from an index, including itself"""
        def _generate_next_corner_array():
            next_corner = [None] * len(self)
            next_corner[0] = 0 # assuming first vertex is a corner
                               # valid if path generate in potrace manner
            for i in ([0] + range(len(self)-1, 0, -1)):
                if self.direction(i) == self.direction(i-1):
                    next_corner[i-1] = next_corner[i]
                else:
                    next_corner[i-1] = (i-1) % len(self)
            return next_corner
        try:
            self.next_corner_array
        except AttributeError:
            self.next_corner_array = _generate_next_corner_array()
        return self.next_corner_array[index]

    @mod_index
    @memoize
    def direction(self, index):
        """At a vertex, determine the direction in which the path goes to arrive at that vertex"""
        v1 = self[index]
        v2 = self[index-1]
        diff = (v2[0] - v1[0], v2[1] - v1[1])
        return diff

    @property
    @memoize
    def directions(self):
        return [self.direction(i) for i in range(len(self))]

    def get_last_straights(self):
        """Returns an array of the last point on a straight line from an index"""
        def constraing_check_hit():
            pass
        def update_constraints():
            pass
        first_time_through_i_loop = True
        pivot_k = [None] * len(self)
        for i in reversed(range(len(self))):
            path_directions = set()
            for k in self.cycrange(i+2, i+len(self)):
                if first_time_through_i_loop:
                    first_time_through_i_loop = False
                elif cyclic(k, i, pivot_k[i+1]):
                    break
                if len(path_directions) == 4:
                    break
                if constraint_check_hit():
                    break
                update_constraints()
            pivot_k[i] = (k-1) % len(self)

        # cleanup


def test_Cycle():
    p = Cycle([(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(4,4),(5,4),(5,3),(4,3),(4,2),(3,2),(2,2),(2,1)])
    for x in p:
        print x
    for i in [0, 3, -3, -123, 34, 1231231232]:
        print i, p[i]
    print p[0:]
    print p[3:]
    print p[:-1]
    print p[10:20]
    print p.cycrange(10, 16)

def test_Path():
    p = Path([(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(4,4),(5,4),(5,3),(4,3),(4,2),(3,2),(2,2),(2,1)])
    for x in p:
        print x
    for i in [0, 3, -3, -123, 34, 1231231232]:
        print i, p[i]
    print p[0:]
    print p[3:]
    print p[:-1]
    print p[10:20]
    print p.direction(0)
    print p.direction(-14)
    print p.direction(3)
    print p.next_corner(0)
    print p.next_corner(14)
    print p.directions



if __name__ == '__main__':
    test_Cycle()
    test_Path()
