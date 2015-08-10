__author__ = 'zshimanchik'
import math
import random

from NeuralNetwork.NeuralNetwork import NeuralNetwork


class Primitive():
    DEBUG = True
    MIN_BRAIN_STIMULATION = 0.1
    MAX_BRAIN_STIMULATION = 0.2
    BRAIN_STIMULATION_FILTER_THRESHOLD = 0.5
    RANDOM_VALUE_FOR_ANSWER = 0.2
    SENSOR_COUNT = 8
    MIN_SENSOR_RADIUS = 20
    MAX_SENSOR_RADIUS = 60
    MAX_SENSOR_DISTANCE = MAX_SENSOR_RADIUS

    def __init__(self):
        self.sensors = Primitive._generate_sensors(sensor_count=Primitive.SENSOR_COUNT, x=100, y=100, radius=60)
        self.state = 0
        self.stimulation = 0
        self.prev_influence = 0
        self.brain_stimulation = 0
        self.middle_x, self.middle_y = 20, 20

        self.idle_time = 0
        self.random_plan = []
        self.first_state = True

        self.brain = NeuralNetwork([len(self.sensors), 23, len(self.sensors) * 2], Primitive.RANDOM_VALUE_FOR_ANSWER)
        # self.brain = NetworkTest.make_net(self.sensor_count)

    @staticmethod
    def _generate_sensors(sensor_count, x, y, radius):
        angle_peace = math.pi * 2 / sensor_count
        return [[math.cos(i * angle_peace) * radius + x + random.randint(-5, 5), math.sin(i * angle_peace) * radius + y]
                for i in range(sensor_count)]

    def update(self, sensors_values):
        answer = self.brain.calculate(sensors_values)
        # self.move([(answer[i], answer[i + 1]) for i in range(0, len(answer), 2)])
        self.move([(x,y) for x, y in zip(answer[::2], answer[1::2])])
        if self.DEBUG:
            print(("{:.4f} " * len(answer)).format(*answer))

    def change_state(self, influence_value):
        self.state += influence_value
        self.state = max(self.state, -1.0)
        self.state = min(self.state, 1.0)

        self.stimulation = influence_value - self.prev_influence
        self.prev_influence = influence_value
        if self.DEBUG:
            print("stimulation={:.6f}".format(self.stimulation))
        # TODO can it be deleted?
        if self.first_state:
            self.first_state = False
            return

        # sign of self.stimulation
        sign = (self.stimulation > 0) - (self.stimulation < 0)
        abs_stimulation = abs(self.stimulation)
        self.brain_stimulation = (abs_stimulation < Primitive.BRAIN_STIMULATION_FILTER_THRESHOLD) * sign \
                                 * min(max(Primitive.MIN_BRAIN_STIMULATION, abs_stimulation), Primitive.MAX_BRAIN_STIMULATION)
        self.brain.teach_considering_random(self.brain_stimulation)

    def move(self, position_diffs):
        assert len(position_diffs) == len(self.sensors)
        for sensor, diff in zip(self.sensors, position_diffs):
            sensor[0] += diff[0]
            sensor[1] += diff[1]
        self.check_shape()

    def check_shape(self):
        self.middle_x = sum(sensor[0] for sensor in self.sensors) / len(self.sensors)
        self.middle_y = sum(sensor[1] for sensor in self.sensors) / len(self.sensors)

        polar_sensors = []
        for sensor in self.sensors:
            diff_x = sensor[0] - self.middle_x
            diff_y = sensor[1] - self.middle_y
            angle = math.atan2(diff_y, diff_x)
            if angle < 0:
                angle += math.pi * 2
            length = math.sqrt(diff_x ** 2 + diff_y ** 2)
            polar_sensors.append([angle, length])

        prev = polar_sensors[-1]
        for sensor in polar_sensors:
            if prev[0] + (sensor[0] > prev[0]) * math.pi * 2 < sensor[0] + math.pi:
                sensor[0], prev[0] = prev[0], sensor[0]
            sensor[1] = max(sensor[1], Primitive.MIN_SENSOR_RADIUS)
            sensor[1] = min(sensor[1], Primitive.MAX_SENSOR_RADIUS)
            prev = sensor

        self.sensors = [[math.cos(angle) * length + self.middle_x, math.sin(angle) * length + self.middle_y]
                        for angle, length in polar_sensors]
        for i in range(-1, len(self.sensors) - 1, 1):
            prev = self.sensors[i]
            cur = self.sensors[i + 1]
            distance = math.sqrt((cur[0] - prev[0]) ** 2 + (cur[1] - prev[1]) ** 2)
            if distance > Primitive.MAX_SENSOR_DISTANCE:
                dd = (distance - Primitive.MAX_SENSOR_DISTANCE) / 2.0
                vec = (cur[0] - prev[0]) / distance * dd, (cur[1] - prev[1]) / distance * dd
                prev[0] += vec[0]
                prev[1] += vec[1]
                cur[0] -= vec[0]
                cur[1] -= vec[1]


