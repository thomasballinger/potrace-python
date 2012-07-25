import Image
import numpy

import pylab

BLACK = True
WHITE = False

#TODO address the implications of centers vs corners

def testData():
    im = Image.open('data1.bmp')
    a = numpy.zeros(im.size, dtype=numpy.bool)
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            a[i,j] = im.getpixel((i,j))
    padded = numpy.zeros((a.shape[0]+2, a.shape[1]+2), dtype=numpy.bool)
    padded[1:-1, 1:-1] = a
    return padded

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

def problem_test_data():
    a = numpy.array([[0,0,0,0,0],
                     [0,1,1,1,0],
                     [0,1,0,1,0],
                     [0,0,1,1,0],
                     [0,0,0,0,0]], dtype=numpy.bool)
    return a

def neighbors(spot, array):
    neighbors = []
    for row_offset, col_offset in [(-1,0), (0,-1), (0,1), (1,0)]:
        pos = (spot[0]+row_offset, spot[1]+col_offset)
        if 0 <= pos[0] < array.shape[0] and 0 <= pos[1] < array.shape[1]:
            neighbors.append(pos)
    #print 'neighbors', neighbors
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
    #print pretty_headings[heading], heading
    forward_left  = (black[0] + heading[0], black[1] + heading[1])
    forward_right = (white[0] + heading[0], white[1] + heading[1])
    #print 'forward spaces are:'
    #print forward_left, array[forward_left]
    #print forward_right, array[forward_right]
    if array[forward_left] and array[forward_right]:
        #print 'turn_right'
        return forward_right, white
    if array[forward_left] and not array[forward_right]:
        #print 'straight'
        return forward_left, forward_right
    if not array[forward_left] and not array[forward_right]:
        #print 'turn_left'
        return black, forward_left
    if not array[forward_left] and array[forward_right]:
        #print 'turn_left' #TODO add turn policies here
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
    #print 'edges', edges
    horiz_edges = [sorted([v1, v2], key=lambda x: x[1]) for v1, v2 in edges if v1[0] == v2[0]]
    #print 'horiz_edges', horiz_edges
    edge_rows_by_column = [[line[0][0] for line in horiz_edges if line[0][1] == column] for column in set([edge[0][0] for edge in horiz_edges])]
    columns = set([edge[0][1] for edge in horiz_edges])
    #print 'columns:', columns
    edge_rows_by_column = dict([(column, [line[0][0] for line in horiz_edges if line[0][1] == column]) for column in columns])
    #print 'edge rows by column:', edge_rows_by_column
    sorted_edge_rows_by_column = [sorted(edge_rows_by_column[column]) for column in columns]
    #print "sorted_edge_rows_by_column:", sorted_edge_rows_by_column
    total = sum([sum([h-l for l, h in zip(rows[::2], rows[1::2])]) for rows in sorted_edge_rows_by_column])
    #print 'total', total
    return total

def invert_path_enclosed_region(array, path):
    edges = [(v1, v2) for v1, v2 in zip(path, path[1:]+path[:1])]
    #print 'edges', edges
    horiz_edges = [sorted([v1, v2], key=lambda x: x[1]) for v1, v2 in edges if v1[0] == v2[0]]
    #print 'horiz_edges', horiz_edges
    edge_rows_by_column = [[line[0][0] for line in horiz_edges if line[0][1] == column] for column in set([edge[0][0] for edge in horiz_edges])]
    columns = set([edge[0][1] for edge in horiz_edges])
    #print 'columns:', columns
    edge_rows_by_column = dict([(column, [line[0][0] for line in horiz_edges if line[0][1] == column]) for column in columns])
    #print 'edge rows by column:', edge_rows_by_column
    for column in columns:
        edge_rows_by_column[column].sort()
    #print "sorted_edge_rows_by_column:", edge_rows_by_column
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
    start_positions = set()
    counter = 0
    while True:
        blacks = numpy.where(array)
        whites = numpy.where(array==False)
        #print blacks
        if not blacks[0].any():
            print "Image is completely white"
            break
        first_black = (blacks[0][0], blacks[1][0])
        #print numpy.array(array, dtype=numpy.int)
        first_white = first_neighbor(first_black, False, array)
        print 'working the path that starts and ends at processing', (first_black, first_white)
        if first_black in start_positions:
            raw_input(str(counter))
            counter += 1
        start_positions.add(first_black)
        cur_pos = (first_black, first_white)
        path = [get_vertex(*cur_pos)]
        positions = set()
        while True:
            new_pos = get_action(cur_pos[0], cur_pos[1], array)
            print new_pos
            vertex = get_vertex(*new_pos)
            print 'vertex:', vertex
            #print path
            s = scale = 3
            temp = numpy.array(array, dtype=numpy.int)
            temp[cur_pos[0]] = 5
            temp = numpy.array(temp[max(0, vertex[0]-s):min(temp.shape[0], vertex[0]+s),
                     max(0, vertex[1]-s):min(temp.shape[1], vertex[1]+s)],
                     dtype=numpy.int)
            print temp
            if vertex in path:
                print 'repeating vertex!', vertex
            if new_pos in positions:
                print 'repeat position!'
                break
            positions.add(cur_pos)
            path.append(vertex)
            cur_pos = new_pos
        #print path
        #print numpy.array(array, dtype=numpy.int)
        area = get_interior_area(path)
        #print 'path', path
        #print 'area enclosed by path:', area
        path_areas[tuple(path)] = area
        paths.append(path)
        array = invert_path_enclosed_region(array, path)
        #raw_input()
        #print numpy.array(array, dtype=numpy.int)
    #todo: descpeckling here, filter by path area
    for path in paths:
        print path, path_areas[tuple(path)]
    return paths

def get_polygons(paths):
    print paths
    # find straight lines? page 6 of technical paper

def display_array(array):
    from pylab import imshow
    imshow(array)

def display_paths(paths):
    from matplotlib import pyplot

    def zoom_out():
        xmin, xmax = pyplot.xlim()
        ymin, ymax = pyplot.ylim()
        xsize = xmax - xmin
        ysize = ymax - ymin
        pyplot.xlim(xmin-(xsize/8), xmax+(xsize/8))
        pyplot.ylim(ymin-(ysize/8), ymax+(ysize/8))

    for path in paths:
        print zip(*path)
        pyplot.plot(*zip(*(path+[path[0]])))
    zoom_out()
    pyplot.show()

def padded(array):
    new_array = numpy.zeros((array.shape[0]+2, array.shape[1]+2), dtype=numpy.bool)
    new_array[1:-1, 1:-1] = array
    return new_array

if __name__ == '__main__':
    #im = simple_test_data()
    #im = problem_test_data()
    im = testData()
    array = padded(im)
    paths = get_paths(im)
    thresh = 20
    bigpaths = [path for path in paths if get_interior_area(path) > thresh]
    print numpy.array(numpy.rot90(array), dtype=numpy.int)
    display_paths(bigpaths)

    polygons = get_polygons(paths)

