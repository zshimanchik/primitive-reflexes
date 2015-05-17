__author__ = 'arch'
import math
import random
from NeuralNetwork.NeuralNetwork import NeuralNetwork
import NetworkTest


class Primitive():
    promotion_filter = 0.015
    norma = 0.005

    def __init__(self):
        self.x = 89
        self.y = 120
        self.size = 30
        self.sensor_count = 16
        self.state = 0
        self.promotion = 0
        self.prev_delta = 0

        self.average_promotion = 0
        self.average_promotion_size = 10.0
        self._prev_step_average_promotion_ration = (self.average_promotion_size - 1.0) / self.average_promotion_size
        self.scaled_promotion = 0

        self.idle_time = 0
        self.random_plan = []
        self.first_state = True


        self.brain = NeuralNetwork([self.sensor_count, 10, 2], learn_rate=0.05)
        # self.brain = NetworkTest.make_net(self.sensor_count)

    def sensors_positions(self):
        res = []
        for i in range(self.sensor_count):
            angle = i * math.pi * 2 / self.sensor_count
            res.append((math.cos(angle) * self.size + self.x, math.sin(angle) * self.size + self.y))
        return res

    def update(self, sensors_values):
        answer = self.brain.calculate(sensors_values)
        print("inp={} answ={:.6f}, {:.6f}".format(sensors_values, answer[0], answer[1]))

        if abs(self.promotion) < 0.000001:
            self.idle_time += 1
        else:
            self.idle_time = 0

        # if self.idle_time > 10:
        #     if not len(self.random_plan):
        #         self.random_plan = [random.random() * 2.0 - 1.0] * random.randint(4, 10)
        #
        # if len(self.random_plan):
        #     answer[0] += self.random_plan.pop()

        # self._move(answer[0]*2, answer[1]*2)
        # self._grow_up(answer[2]*2)
        self.move(answer[0], answer[1])

    def change_state(self, delta):
        self.state += delta
        self.state = max(self.state, -1.0)
        self.state = min(self.state, 1.0)

        self.promotion = delta - self.prev_delta
        self.prev_delta = delta
        print "promotion={:.6f}".format(self.promotion)

        if not self.first_state:

            # filter huge spades
            if abs(self.promotion) < Primitive.promotion_filter:
                self.average_promotion = self.average_promotion * self._prev_step_average_promotion_ration \
                                     + abs(self.promotion) / self.average_promotion_size

                if self.average_promotion != 0:
                    self.scaled_promotion = self.promotion / abs(self.average_promotion) * Primitive.norma
                else:
                    self.scaled_promotion=0

                # if abs(self.scaled_promotion) > Primitive.promotion_filter:
                #     self.scaled_promotion = math.copysign(self.promotion_filter, self.scaled_promotion)
                #     print("{:.6f} - {:.6f} - {:.6f} - was cut".format(self.promotion, self.average_promotion, self.scaled_promotion))
                # else:
                #     print("{:.6f} - {:.6f} - {:.6f}".format(self.promotion, self.average_promotion, self.scaled_promotion))

                if self.promotion == 0:
                    self.scaled_promotion = 0
                else:
                    self.scaled_promotion = math.copysign(0.004, self.promotion)

                self.brain.teach(-self.scaled_promotion)
            else:
                print("{:.6f} - {:.6f} - filtered".format(self.promotion, self.average_promotion))
        else:
            self.average_promotion = abs(self.promotion)
            self.first_state = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def _grow_up(self, d_size):
        self.size += d_size
        self.size = max(self.size, 14)
        self.size = min(self.size, 40)
