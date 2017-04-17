import math
import time

from primitive import Primitive

BLACK = (0.0, )
RED = (0.0, )
GREEN = (1.0, )
BLUE = (0.0, )


class World:
    def __init__(self, width, height, mouse):
        self.prim = Primitive()
        self.width = width
        self.height = height
        self.mouse = mouse
        self.time = 0
        self.prev_time = time.time()
        self.performance = 0

    def update(self):
        self.time += 1
        if self.time % 100 == 0:
            now = time.time()
            self.performance = now - self.prev_time
            # print("calc_time={}".format(self.performance))
            self.prev_time = now

        self.update_primitive_position()
        sensors_values = [v for x, y in self.prim.sensors_positions() for v in self.get_sensor_value(x, y)]
        self.prim.sensor_values = sensors_values
        influence_value = self.get_influence_value(self.prim)
        self.prim.update(sensors_values, influence_value)

    def update_primitive_position(self):
        if self.prim.x < 0:
            self.prim.x = self.width - 10
        if self.prim.x > self.width:
            self.prim.x = 10

        if self.prim.y < 0:
            self.prim.y = self.height - 10
        if self.prim.y > self.height:
            self.prim.y = 10

    def get_sensor_value(self, x, y):
        """
        return value vector with values in bound [0;1]
        """
        if not self.mouse.pressed():
            return BLACK

        distance = math.hypot(self.mouse.x - x, self.mouse.y - y)
        smell_strength = max(0, 1 - distance / self.mouse.area_size) ** 2

        if self.mouse.but1_pressed:
            smell = GREEN
        elif self.mouse.but2_pressed:
            smell = RED
        elif self.mouse.but3_pressed:
            smell = BLUE
        else:
            smell = BLACK

        smell = [x*smell_strength for x in smell]
        return smell

    def get_influence_value(self, prim):
        return self.get_sensor_value(prim.x, prim.y)[0]
        # return sum(self.prim.sensor_values[1::3]) * 10
        # return self.prim.sensor_values[1] * 10
