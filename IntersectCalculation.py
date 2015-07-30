__author__ = 'zshimanchik'
import math
FRAGMENTS_COUNT = 30
POINTS_COUNT = FRAGMENTS_COUNT ** 2


def _frange(start, stop, step):
    r = float(start)
    while r < stop:
        yield r
        r += step


def _points_generator(circle_center, circle_radius):
    step_size = float(circle_radius * 2) / FRAGMENTS_COUNT
    for y in _frange(circle_center[1] - circle_radius, circle_center[1] + circle_radius + step_size, step_size):
        for x in _frange(circle_center[0] - circle_radius, circle_center[0] + circle_radius + step_size, step_size):
            yield x, y


def _generate_line_check_func(point1, point2, point_in_area):
    dy = point2[1] - point1[1]
    dx = point2[0] - point1[0]
    if dx == 0:  # vertical line
        leftward = point_in_area[0] < point1[0]

        def check_func(x, y):
            return leftward == (x < point1[0])

        return check_func
    if dy == 0:  # horizontal line
        below = point_in_area[1] < point1[1]

        def check_func(x, y):
            return below == (y < point1[1])

        return check_func

    angle_koef = dy / dx

    y0 = point1[1] - point1[0] * angle_koef
    is_above = point_in_area[0] * angle_koef + y0 < point_in_area[1]
    def check_func(x, y):
        return is_above == (x * angle_koef + y0 < y)
    return check_func


def calc_triangle_and_circle_intersect(tr_point1, tr_point2, tr_point3, circle_center, circle_radius):
    def is_belong_to_circle(x, y):
        return math.sqrt((circle_center[0]-x)**2 + (circle_center[1]-y)**2) <= circle_radius

    check_functions = [
        _generate_line_check_func(tr_point1, tr_point2, tr_point3),
        _generate_line_check_func(tr_point2, tr_point3, tr_point1),
        _generate_line_check_func(tr_point3, tr_point1, tr_point2),
        is_belong_to_circle
    ]

    def is_belong_to_intersect(point):
        for func in check_functions:
            if not func(*point):
                return False
        return True

    belong_points_count = sum(map(is_belong_to_intersect, _points_generator(circle_center, circle_radius)))
    return float(belong_points_count) / POINTS_COUNT * circle_radius ** 2

def calc_triangle_and_circle_intersect_2(args):
    return calc_triangle_and_circle_intersect(*args)