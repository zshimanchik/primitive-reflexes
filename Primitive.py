__author__ = 'zshimanchik'
import math

from NeuralNetwork.NeuralNetwork import NeuralNetwork


class Primitive():
    debug = not (not __debug__ or not False)
    stimulation_filter = 0.015
    fixed_stimulation = 0.004
    norma = 0.005

    def __init__(self):
        self.x = 89
        self.y = 120
        self.size = 30
        self.sensor_count = 16
        self.state = 0
        self.stimulation = 0
        self.prev_influence_delta = 0
        self.scaled_stimulation = 0

        self.idle_time = 0
        self.random_plan = []
        self.first_state = True

        self.brain = NeuralNetwork([self.sensor_count, 10, 3], learn_rate=0.05)
        # self.brain = NetworkTest.make_net(self.sensor_count)

    def sensors_positions(self):
        res = []
        for i in range(self.sensor_count):
            angle = i * math.pi * 2 / self.sensor_count
            res.append((math.cos(angle) * self.size + self.x, math.sin(angle) * self.size + self.y))
        return res

    def update(self, sensors_values):
        answer = self.brain.calculate(sensors_values, random_value=0.1)
        if self.debug:
            print("inp={} answ={:.6f}, {:.6f}, {:.6f}".format(sensors_values, answer[0], answer[1], answer[2]))

        if abs(self.stimulation) < 0.000001:
            self.idle_time += 1
        else:
            self.idle_time = 0

        self.move(answer[0], answer[1])
        self.grow_up(answer[2])

    def change_state(self, influence_delta):
        self.state += influence_delta
        self.state = max(self.state, -1.0)
        self.state = min(self.state, 1.0)

        self.stimulation = influence_delta - self.prev_influence_delta
        self.prev_influence_delta = influence_delta
        if self.debug:
            print("stimulation={:.6f}".format(self.stimulation))

        if self.first_state:
            self.first_state=False
            return

        # filter huge spades
        if abs(self.stimulation) < Primitive.stimulation_filter:
            # signum(self.stimulation) * fixed_stimulation
            self.scaled_stimulation = ((self.stimulation > 0) - (self.stimulation < 0)) * Primitive.fixed_stimulation
            self.brain.teach_considering_random(self.scaled_stimulation)
        else:
            if self.debug:
                print("{:.6f} - filtered".format(self.stimulation))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def grow_up(self, d_size):
        self.size += d_size
        self.size = max(self.size, 14)
        self.size = min(self.size, 40)
