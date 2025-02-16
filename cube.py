import curses
import time
import math

def complexHarmonizedSpin(x_angle, y_angle, z_angle, factor):
    '''Combining multiple sine and cosine waves with different frequencies and amplitudes gives a rich, harmonized rotational effect'''

    x_angle = math.sin(0.01 * factor) * 40 + math.cos(0.005 * factor) * 30
    y_angle = math.sin(0.015 * factor) * 50 + math.cos(0.01 * factor) * 20
    z_angle = math.sin(0.02 * factor) * 60 + math.cos(0.02 * factor) * 10

    return x_angle, y_angle, z_angle

def rotate(x_angle, y_angle, z_angle, x, y, z):
    '''Rotates vector around x, y, z axes by given angles'''
    # Rotate around x
    first_x = x
    first_y = y * math.cos(x_angle) + z * (-math.sin(x_angle))
    first_z = y * math.sin(x_angle) + z * math.cos(x_angle)

    # Rotate around y
    second_x = first_x * math.cos(y_angle) + first_z * math.sin(y_angle)
    second_y = first_y
    second_z = first_x * (-math.sin(y_angle)) + first_z * math.cos(y_angle)

    # Rotate around z
    third_x = second_x * math.cos(z_angle) + second_y * (-math.sin(z_angle))
    third_y = second_x * math.sin(z_angle) + second_y * math.cos(z_angle)
    third_z = second_z

    return third_x, third_y, third_z

def fill_area(stdscr, x0, y0, x1, y1, x2, y2, x3, y3):
    """Fill the area defined by 4 vertices"""
    # Draw edges and store their points
    edge1 = get_line_points(x0, y0, x1, y1)
    edge2 = get_line_points(x1, y1, x2, y2)
    edge3 = get_line_points(x2, y2, x3, y3)
    edge4 = get_line_points(x3, y3, x0, y0)

    # Merge all edges into a list of points
    edges = edge1 + edge2 + edge3 + edge4
    edges = list(set(edges))  # Remove duplicates

    # Fill area between edges
    y_min = min(y0, y1, y2, y3)
    y_max = max(y0, y1, y2, y3)

    for y in range(y_min, y_max + 1):
        # Find intersections with the scanline
        intersections = sorted([x for x, yy in edges if yy == y])
        if len(intersections) >= 2:
            for x in range(intersections[0], intersections[-1] + 1):
                try:
                    stdscr.addstr(y, x, '#')  # y value first!
                except curses.error:
                    pass


def get_line_points(x0, y0, x1, y1):
    """Return all points on a line using Bresenham's algorithm."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while x0 != x1 or y0 != y1:
        points.append((x0, y0))
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    points.append((x1, y1))  # Include the last point

    return points

def project(x, y, z):
    """Project 3D coordinates onto 2D plane and scale to terminal size"""
    # Define terminal size
    width = 100
    height = 50
    
    factor = 20 # Change to scale up and down 
    z += 5   # Translate z away from (0, 0, 0) to avoid Devide-By-Zero

    # Devide by z because camera is at (0, 0, 0) 
    # see: https://stackoverflow.com/questions/724219/how-to-convert-a-3d-point-into-2d-perspective-projection/724243#724243
    new_x = int((x * factor) / z)
    new_y = int((-y * factor) / z)

    # Center in terminal window
    new_x += int(width / 2)
    new_y += int(height / 2)

    return new_x, new_y

def draw_cube(stdscr, vertices):
    """Draw cube in terminal"""
    # Define faces by connecting vertices
    faces = [
        (0, 1, 2, 3),
        (0, 1, 5, 4),
        (4, 5, 6, 7),
        (2, 3, 7, 6),
        (0, 4, 7, 3),
        (1, 5, 6, 2)
    ]

    # Project all 4 vertices of a face to 2d plane and fill the area
    for face in faces:
        first_vertex = vertices[face[0]]
        second_vertex = vertices[face[1]]
        third_vertex = vertices[face[2]]
        fourth_vertex = vertices[face[3]]
        # Project vertices
        x0, y0 = project(*first_vertex)
        x1, y1 = project(*second_vertex)
        x2, y2 = project(*third_vertex)
        x3, y3 = project(*fourth_vertex)
        try:
            fill_area(stdscr, x0, y0, x1, y1, x2, y2, x3, y3)
        except curses.error:
            pass
            
        

def draw_cube_edges(stdscr, vertices):
    """Draw only the edges of the cube in terminal"""
    # Define edges by connecting vertices
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # front face
        (4, 5), (5, 6), (6, 7), (7, 4),  # back face
        (0, 4), (1, 5), (2, 6), (3, 7)   # connecting edges
    ]

    # Draw each edge
    for edge in edges:
        first_vertex = vertices[edge[0]]
        second_vertex = vertices[edge[1]]
        
        # Project vertices
        x0, y0 = project(*first_vertex)
        x1, y1 = project(*second_vertex)
        
        # Draw the line using Bresenham's algorithm
        points = get_line_points(x0, y0, x1, y1)
        for x, y in points:
            try:
                stdscr.addstr(y, x, '#')
            except curses.error:
                pass

def main(stdscr):
    # Hide cursor
    curses.curs_set(False)

    # Get user input for display mode
    stdscr.clear()
    stdscr.addstr(0, 0, "Choose display mode:")
    stdscr.addstr(1, 0, "1. Filled cube")
    stdscr.addstr(2, 0, "2. Edges only")
    stdscr.addstr(3, 0, "Enter your choice (1 or 2): ")
    stdscr.refresh()
    
    while True:
        choice = stdscr.getch()
        if choice in [ord('1'), ord('2')]:
            break
    
    display_mode = 'filled' if choice == ord('1') else 'edges'
    
    # Clear the screen after choice
    stdscr.clear()
    stdscr.refresh()

    # Define cube dimensions (even numbers only!)
    width = 4
    height = 4
    depth = 4

    half_width = width / 2
    half_height = height / 2
    half_depth = depth / 2

    # Define initial cube vertices around (0, 0, 0)
    vertices = [
        (-half_width, -half_height, -half_depth),   # 0 - l b f
        (half_width, -half_height, -half_depth),    # 1 - r b f
        (half_width, half_height, -half_depth),     # 2 - r t f
        (-half_width, half_height, -half_depth),    # 3 - l t f
        (-half_width, -half_height, half_depth),    # 4 - l b b
        (half_width, -half_height, half_depth),     # 5 - r b b
        (half_width, half_height, half_depth),      # 6 - r t b
        (-half_width, half_height, half_depth)      # 7 - l t b
    ]

    x_angle, y_angle, z_angle = 0, 0, 0
    factor = 0

    # Draw cube loop
    while 1:
        stdscr.clear()

        # Rotate vertices and redraw cube
        rotated_vertices = []
        for vertex in vertices:
            rotated_vertex = rotate(x_angle, y_angle, z_angle, *vertex)
            rotated_vertices.append(rotated_vertex)
        
        if display_mode == 'filled':
            draw_cube(stdscr, rotated_vertices)
        else:
            draw_cube_edges(stdscr, rotated_vertices)
            
        stdscr.refresh()

        # Increasing angles
        x_angle, y_angle, z_angle = complexHarmonizedSpin(x_angle, y_angle, z_angle, factor)

        factor += 0.1   # Rotation angle factor

        time.sleep(0.04)   # Refresh rate

if __name__ == "__main__":
    curses.wrapper(main)