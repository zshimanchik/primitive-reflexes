__author__ = 'zshimanchik'
from collections import deque
import math
import random

# from NeuralNetwork.NeuralNetwork import NeuralNetwork
from neural_network.neural_network import NeuralNetwork

TWO_PI = math.pi * 2


class Primitive():
    DEBUG = False
    MIN_BRAIN_STIMULATION = 0.01
    MAX_BRAIN_STIMULATION = 0.1
    BRAIN_STIMULATION_FILTER_THRESHOLD = 0.3
    RANDOM_VALUE_FOR_ANSWER = 0.1

    MEMORY_SIZE_FOR_LEARNING = 5000
    TEACH_SIZE = 0.7
    START_CHANCE_TO_MOVE_RANDOM = 0.5
    MIN_CHANCE_TO_MOVE_RANDOM = 0.2
    CHANCE_TO_MOVE_RANDOM_FACTOR = 0.99

    SENSOR_DIMENSION = 1
    MOVE_DIMENSION = 6

    def __init__(self):
        self.x = 89
        self.y = 120
        self.angle = 0
        self.size = 30
        self.sensor_count = 5
        self.sensor_values = []
        self.state = 0
        self.stimulation = 0
        self.influence_value = 0
        self.confidence = 0
        self.plan_len = 0
        self.prev_influence = 0
        self.brain_stimulation = 0
        self._chance_to_move_random = self.START_CHANCE_TO_MOVE_RANDOM

        self.idle_time = 0
        self.plan = deque()
        self._memory = []  # list of tuples (sensors_values, move, reward, new_sensors_values)
        self.input_layer_size = self.sensor_count * self.SENSOR_DIMENSION + self.MOVE_DIMENSION
        self._last_sensor_values = [0] * self.sensor_count * self.SENSOR_DIMENSION
        self._last_move = [0] * self.MOVE_DIMENSION
        self._all_movements = self._gen_all_movements()

        self.brain = NeuralNetwork([self.input_layer_size, 6, 1])
        self.brain.calculate([[0] * self.input_layer_size])

    def sensors_positions(self):
        res = []
        for i in range(self.sensor_count):
            angle = self.angle + i * math.pi * 2 / self.sensor_count
            res.append((math.cos(angle) * self.size + self.x, math.sin(angle) * self.size + self.y))
        return res

    def update(self, sensors_values, influence_value):
        self.sensor_values = sensors_values
        self.influence_value = influence_value

        reward = influence_value / 10.0
        # if reward > 0:
        self._memory.append((self._last_sensor_values, self._last_move, reward, self.sensor_values))

        if len(self._memory) >= self.MEMORY_SIZE_FOR_LEARNING:
            self._learn()

        if random.random() < self._chance_to_move_random:
            move = random.choice(self._all_movements)
            move_index = move.index(max(move))
            answers = self.brain.calculate([sensors_values + move])
            self.confidence = answers[0][0]
        else:
            inputs = [sensors_values + move for move in self._all_movements]
            answers = self.brain.calculate(inputs)
            move, answer = max(zip(self._all_movements, answers), key=lambda x: x[1][0])
            move_index = move.index(max(move))
            if self.DEBUG:
                print('=====')
                print('\n'.join('{} => {:.6f}'.format(format_list(x), a[0]) for x, a in zip(inputs, answers)))
                # print(format_list(answers.reshape(answers.size)))
                print(format_list(sensors_values), move_index, format_list(answer))
            self.confidence = answer[0]

        self._last_sensor_values = sensors_values
        self._last_move = move
        self.move(move_index)

    def _gen_all_movements(self):
        ress = []
        zeros = [0] * self.MOVE_DIMENSION
        for i in range(self.MOVE_DIMENSION):
            res = zeros.copy()
            res[i] = 1
            ress.append(res)
        return ress

    def _learn(self):
        print("learn")
        if self._chance_to_move_random >= self.MIN_CHANCE_TO_MOVE_RANDOM:
            self._chance_to_move_random *= self.CHANCE_TO_MOVE_RANDOM_FACTOR

        data = self._choice_chunk_and_shuffle(self.TEACH_SIZE)

        teach_inputs = []
        teach_target = []
        for state, move, reward, new_state in data:
            best_reward = self._get_best_reward(new_state)
            teach_inputs.append(state + move)
            teach_target.append([max(best_reward, reward)])

        self.brain.train(teach_inputs, teach_target)
        self._memory.clear()

    def _choice_chunk_and_shuffle(self, chunk_size=0.7):
        random.shuffle(self._memory)
        new_len = int(len(self._memory) * chunk_size)
        return self._memory[:new_len]


    def _get_best_reward(self, state):
        inputs = [state + move for move in self._all_movements]
        answers = self.brain.calculate(inputs)
        return answers[:,0].max()


    def _get_brain_stimulation(self, influence_value):
        """
        brain must be calculated before using this method!!
        """
        self.influence_value = influence_value
        self.state += influence_value
        self.state = max(self.state, -1.0)
        self.state = min(self.state, 1.0)

        self.stimulation = influence_value - self.prev_influence
        self.prev_influence = influence_value
        if self.DEBUG:
            print("stimulation={:.6f}".format(self.stimulation))

        # sign of self.stimulation
        sign = (self.stimulation > 0) - (self.stimulation < 0)
        abs_stimulation = abs(self.stimulation)
        self.brain_stimulation = (abs_stimulation < Primitive.BRAIN_STIMULATION_FILTER_THRESHOLD) * sign \
                                 * min(abs_stimulation, Primitive.MAX_BRAIN_STIMULATION)
        return self.brain_stimulation
        # self.brain.teach_considering_random(self.brain_stimulation)

    moves = [
        (1, -1),
        (1, 0),
        (1, 1),
        (-1, 1),
        (-1, 0),
        (-1, -1),
    ]

    def move(self, move_index):
        assert 0 <= move_index <= 5
        length, rotate_angle = self.moves[move_index]
        self.angle = (self.angle + rotate_angle * length * 0.03) % TWO_PI
        self.x += math.cos(self.angle) * length*0.5
        self.y += math.sin(self.angle) * length*0.5

def format_list(array):
    return '[' + ', '.join("{:.6f}".format(x) for x in array) + ']'