
import sys
import functools

#TODO separate conditions of eqality from this
def cyclic_in_order(a, b, c):
    """Returns True if points are in order on a circle, a <= b < c < a"""
    if a <= c:
        return (a <= b and b < c)
    else:
        return (a <= b or b < c)

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
            mod_j = j % len(self)
            print "mod_i", mod_i, "mod_j", mod_j
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
        class Vector(object):
            def __init__(self, p1=(0,0), p2=(0,0)):
                self.x = p2[0] - p1[0]
                self.y = p2[1] - p1[1]
            def __repr__(self):
                return '<%s, %s>' % (self.x, self.y)
        def xprod(v1, v2):
            return v1.x * v2.y - v1.y * v2.x
        constraints = [Vector([0,0],[0,0]), Vector([0,0],[0,0])]
        def constraint_check_hit(i, k):
            print 'points i:', i, self[i], 'k:', k, self[k]
            print 'constraints:', constraints
            cur = Vector(self[i], self[k])
            print 'cur:', cur
            if xprod(constraints[0], cur) < 0:
                print 'constraints[0] fail:', constraints[0], 'cross', cur, ' < 0'
                raw_input()
                return True
            if xprod(constraints[1], cur) > 0:
                print 'constraints[1] fail:', constraints[1], 'cross', cur, ' > 0'
                raw_input()
                return True
            else:
                print 'constraints[0] ok:', constraints[0], 'cross', cur, ' !< 0'
                print 'constraints[1] ok:', constraints[1], 'cross', cur, ' !> 0'
                print 'not violated yet...'
                raw_input()
                return False
        def update_constraints(i, k):
            print 'updating constraints...'
            cur = Vector(self[i], self[k])
            if abs(cur.x) <= 1 and abs(cur.y) <= 1:
                return
            off = Vector()
            off.x = cur.x + (1 if cur.y>=0 and (cur.y>0 or cur.x<0) else -1)
            print 'added to x:', (1 if cur.y>=0 and (cur.y>0 or cur.x<0) else -1)
            off.y = cur.y + (1 if cur.x<=0 and (cur.x<0 or cur.y<0) else -1)
            print 'added to y:', (1 if cur.x<=0 and (cur.x<0 or cur.y<0) else -1)
            if xprod(constraints[0], off) >= 0:
                constraints[0].x, constraints[0].y = off.x, off.y

            off.x = cur.x + (1 if cur.y<=0 and (cur.y<0 or cur.x<0) else -1)
            print 'added to x:', (1 if cur.y<=0 and (cur.y<0 or cur.x<0) else -1)
            off.y = cur.y + (1 if cur.x>=0 and (cur.x>0 or cur.y<0) else -1)
            print 'added to y:', (1 if cur.x>=0 and (cur.x>0 or cur.y<0) else -1)
            if xprod(constraints[1], off) <= 0:
                constraints[1].x, constraints[1].y = off.x, off.y

        pivot_k = [None] * len(self)
        for i in reversed(range(len(self))):
            print 'now looking for last straight from i', i, self[i]
            raw_input('- - - -')
            constraints[0].x = constraints[0].y = 0
            constraints[1].x = constraints[1].y = 0
            #for k in self.cycrange(i+2, i+len(self)):
            k = (i + 2) % len(self)
            while k != i:
                print 'now checking k', k, self[k]
                if i == len(self)-1: #first time through loop
                    pass
                elif cyclic_in_order(k, i, pivot_k[i+1]):
                    print 'found bad k because after our last iteration says so'
                    break
                if len(set(self.directions[i+1:k+1])) == 4:
                    print 'found bad k because all directions used'
                    break
                if constraint_check_hit(i, k):
                    break
                update_constraints(i, k)
                print 'now constraints are', constraints
                #continue
                k = (k+1) % len(self)
            pivot_k[i] = (k-1) % len(self)
        # cleanup
        furthest_straight_vertex = [None] * len(self)
        j = pivot_k[len(self)-1]
        furthest_straight_vertex[len(self)-1] = j
        for i in reversed(range(len(self)-1)):
            if cyclic_in_order(i+1, pivot_k[i], j):
                j = pivot_k[i]
            furthest_straight_vertex[i] = j

        i = len(self)-1
        while cyclic_in_order((i+1) % len(self), j, furthest_straight_vertex[i]):
            i -= 1
            furthest_straight_vertex[i] = j
        return furthest_straight_vertex

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
    #p = Path([(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(4,4),(5,4),(5,3),(4,3),(4,2),(3,2),(2,2),(2,1)])
    p = Path([(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(4,4),(5,4),(5,3),(4,3),(4,2),(3,2),(2,2),(2,1)])
    p = []
    s = 6
    p.extend([(x,1) for x in range(1,s)])
    p.extend([(s, y) for y in range(1,s)])
    p.extend([(x, s) for x in reversed(range(2,s+1))])
    p.extend([(1, y) for y in reversed(range(2,s+1))])
    p = Path(p)
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
    s1 =  p.get_last_straights()
    print p
    print '---'
    print [s1]
    print [p[x] for x in s1]
    import old
    print 'old:'
    print old.get_path_options([list(p)])
    print [p[x] for x in old.get_path_options([list(p)])[0]]

if __name__ == '__main__':
    test_Cycle()
    test_Path()
