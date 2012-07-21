import Image
import numpy

BLACK = True
WHITE = False

#TODO address the implications of centers vs corners

def testData():
    return numpy.array(Image.open('data1.bmp'))

def simple_test_data():
    a = numpy.array([[0,0,0,0,0,0],
                     [0,0,1,1,0,0],
                     [0,1,1,1,1,0],
                     [0,1,0,1,0,0],
                     [0,1,1,1,1,0],
                     [0,0,0,0,0,0],
                     [0,0,0,1,0,0],
                     [0,1,1,1,1,0],
                     [0,0,0,0,0,0]], dtype=numpy.bool)
    return a

def neighbors(spot, array):
    neighbors = []
    for row_offset, col_offset in [(-1,0), (0,-1), (0,1), (1,0)]:
        pos = (spot[0]+row_offset, spot[1]+col_offset)
        if 0 <= pos[0] < array.shape[0] and 0 <= pos[1] < array.shape[1]:
            neighbors.append(pos)
    print 'neighbors', neighbors
    return neighbors

def first_neighbor(spot, color, array):
    for pos in neighbors(spot, array):
        if array[pos[0], pos[1]] == color:
            return pos
    else:
        return None

def get_heading(black, white):
    if not (black[0] == white[0] or black[1] == white[1]):
        raise Exception('pixels are not contiguous')
    if black[0]<white[0]: return (0, 1)
    if black[0]>white[0]: return (0, -1)
    if black[1]<white[1]: return (-1, 0)
    if black[1]>white[1]: return (1, 0)
    raise Exception('pixels appear to be the same')

def get_action(black, white, array):
    heading = get_heading(black, white)
    print pretty_headings[heading], heading
    forward_left  = (black[0] + heading[0], black[1] + heading[1])
    forward_right = (white[0] + heading[0], white[1] + heading[1])
    print 'forward spaces are:'
    print forward_left, array[forward_left]
    print forward_right, array[forward_right]
    if array[forward_left] and array[forward_right]:
        print 'turn_right'
        return forward_right, white
    if array[forward_left] and not array[forward_right]:
        print 'straight'
        return forward_left, forward_right
    if not array[forward_left] and not array[forward_right]:
        print 'turn_left'
        return black, forward_left
    if not array[forward_left] and array[forward_right]:
        print 'turn_left' #TODO add turn policies here
        return black, forward_left

pretty_headings = {
        (-1,0):'N',
        (1,0):'S',
        (0,1):'E',
        (0,-1):'W',
        }

def get_vertex(black, white):
    heading = get_heading(black, white)
    if heading == (-1, 0):
        return white
    if heading == (1, 0):
        return (black[0]+1, black[1])
    if heading == (0, 1):
        return (white[0], white[1]+1)
    if heading == (0, -1):
        return black
    raise Exception('bad heading')

def get_interior_area(path):
    edges = [(v1, v2) for v1, v2 in zip(path, path[1:]+path[:1])]
    print 'edges', edges
    horiz_edges = [sorted([v1, v2], key=lambda x: x[1]) for v1, v2 in edges if v1[0] == v2[0]]
    print 'horiz_edges', horiz_edges
    edge_rows_by_column = [[line[0][0] for line in horiz_edges if line[0][1] == column] for column in set([edge[0][0] for edge in horiz_edges])]
    columns = set([edge[0][1] for edge in horiz_edges])
    print 'columns:', columns
    edge_rows_by_column = dict([(column, [line[0][0] for line in horiz_edges if line[0][1] == column]) for column in columns])
    print 'edge rows by column:', edge_rows_by_column
    sorted_edge_rows_by_column = [sorted(edge_rows_by_column[column]) for column in columns]
    print "sorted_edge_rows_by_column:", sorted_edge_rows_by_column
    total = sum([sum([h-l for l, h in zip(rows[::2], rows[1::2])]) for rows in sorted_edge_rows_by_column])
    print 'total', total
    return total

def invert_path_enclosed_region(array, path):
    edges = [(v1, v2) for v1, v2 in zip(path, path[1:]+path[:1])]
    print 'edges', edges
    horiz_edges = [sorted([v1, v2], key=lambda x: x[1]) for v1, v2 in edges if v1[0] == v2[0]]
    print 'horiz_edges', horiz_edges
    edge_rows_by_column = [[line[0][0] for line in horiz_edges if line[0][1] == column] for column in set([edge[0][0] for edge in horiz_edges])]
    columns = set([edge[0][1] for edge in horiz_edges])
    print 'columns:', columns
    edge_rows_by_column = dict([(column, [line[0][0] for line in horiz_edges if line[0][1] == column]) for column in columns])
    print 'edge rows by column:', edge_rows_by_column
    for column in columns:
        edge_rows_by_column[column].sort()
    print "sorted_edge_rows_by_column:", edge_rows_by_column
    for column in columns:
        rows = edge_rows_by_column[column]
        for l, h in zip(rows[::2], rows[1::2]):
            for r in range(l, h):
                array[r, column] = not array[r, column]
    return array

def get_paths(array):
    # find first black/white pixel pair

    # first black pixel
    paths = []
    path_areas = {}
    while True:
        blacks = numpy.where(array)
        whites = numpy.where(array==False)
        print blacks
        if not blacks[0].any():
            print "Image is completely white"
            break
        first_black = (blacks[0][0], blacks[1][0])
        print numpy.array(array, dtype=numpy.int)
        first_white = first_neighbor(first_black, False, array)
        print (first_black, first_white)
        cur_pos = (first_black, first_white)
        path = [get_vertex(*cur_pos)]
        while True:
            new_pos = get_action(cur_pos[0], cur_pos[1], array)
            print new_pos
            vertex = get_vertex(*new_pos)
            print 'vertex:', vertex
            print path
            if vertex in path:
                break
            path.append(vertex)
            cur_pos = new_pos
        print path
        print numpy.array(array, dtype=numpy.int)
        area = get_interior_area(path)
        print area
        path_areas[tuple(path)] = area
        paths.append(path)
        array = invert_path_enclosed_region(array, path)
        print numpy.array(array, dtype=numpy.int)
    #todo: descpeckling here, filter by path area
    for path in paths:
        print path, path_areas[tuple(path)]
    return paths

def get_polygons(paths):
    pass

def display_array(array):
    from pylab import imshow
    imshow(array)

def display_paths(paths):
    from matplotlib import pyplot
    for path in paths:
        print zip(*path)
        pyplot.plot(*zip(*path))
        pyplot.show()

def padded(array):
    new_array = numpy.zeros((array.shape[0]+2, array.shape[1]+2), dtype=numpy.bool)
    new_array[1:-1, 1:-1] = array
    return new_array

if __name__ == '__main__':
    im = simple_test_data()
    #im = testData()
    array = padded(im)
    paths = get_paths(im)
    display_paths(paths)

    #polygons = get_polygons(paths)

