__author__ = 'zshimanchik'
import math

from NeuralNetwork.NeuralNetwork import NeuralNetwork


class Primitive():
    DEBUG = True
    MIN_BRAIN_STIMULATION = 0.04
    MAX_BRAIN_STIMULATION = 0.1
    BRAIN_STIMULATION_FILTER_THRESHOLD = 0.3
    RANDOM_VALUE_FOR_ANSWER = 0.1

    def __init__(self):
        self.x = 89
        self.y = 120
        self.size = 30
        self.sensor_count = 16
        self.sensor_values = []
        self.state = 0
        self.stimulation = 0
        self.prev_influence = 0
        self.brain_stimulation = 0

        self.idle_time = 0
        self.random_plan = []
        self.first_state = True

        self.brain = NeuralNetwork([self.sensor_count * 3, 18, 3], random_value=self.RANDOM_VALUE_FOR_ANSWER)
        # self.brain = NetworkTest.make_net(self.sensor_count)

    def sensors_positions(self):
        res = []
        for i in range(self.sensor_count):
            angle = i * math.pi * 2 / self.sensor_count
            res.append((math.cos(angle) * self.size + self.x, math.sin(angle) * self.size + self.y))
        return res

    def update(self, sensors_values):
        self.sensor_values = zip(sensors_values[::3], sensors_values[1::3], sensors_values[2::3])
        answer = self.brain.calculate(sensors_values)
        if self.DEBUG:
            print("answ={:.6f}, {:.6f}, {:.6f} inp={}".format(answer[0], answer[1], answer[2], self.sensor_values))
        self.move(answer[0], answer[1])
        self.grow_up(answer[2])

    def change_state(self, influence_value):
        self.state += influence_value
        self.state = max(self.state, -1.0)
        self.state = min(self.state, 1.0)

        self.stimulation = influence_value - self.prev_influence
        self.prev_influence = influence_value
        if self.DEBUG:
            print("stimulation={:.6f}".format(self.stimulation))

        if self.first_state:
            self.first_state=False
            return

        # sign of self.stimulation
        sign = (self.stimulation > 0) - (self.stimulation < 0)
        abs_stimulation = abs(self.stimulation)
        self.brain_stimulation = (abs_stimulation < Primitive.BRAIN_STIMULATION_FILTER_THRESHOLD) * sign \
                                 * min(max(Primitive.MIN_BRAIN_STIMULATION, abs_stimulation), Primitive.MAX_BRAIN_STIMULATION)
        self.brain.teach_considering_random(self.brain_stimulation)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def grow_up(self, d_size):
        self.size += d_size
        self.size = max(self.size, 14)
        self.size = min(self.size, 40)
