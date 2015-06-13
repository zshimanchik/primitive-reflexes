from Layer import Layer, InputLayer, ContextLayer
import math
import random


class NeuralNetwork:
    def __init__(self, shape, learn_rate=3.5):
        self.layers = []
        self.shape = shape
        self.time = 0
        self.learn_rate = learn_rate

        self.input_layer = InputLayer(shape[0])

        self.middle_layer = Layer(shape[1], self.input_layer.neurons)
        self.input_layer.listeners.append(self.middle_layer)

        self.output_layer = Layer(shape[2], self.middle_layer.neurons)
        self.middle_layer.listeners.append(self.output_layer)

        # self.context_layer = ContextLayer(shape[1], self.middle_layer.neurons)
        # self.middle_layer.listeners.append(self.context_layer)
        # self.middle_layer.add_input(self.context_layer.neurons)

        self.layers.append(self.input_layer)
        self.layers.append(self.middle_layer)
        self.layers.append(self.output_layer)
        # self.layers.append(self.context_layer)

        # prev_layer = self.input_layer
        # for i in range(1, len(self)):
        #     cur_layer = Layer(shape[i], prev_layer.neurons)
        #     prev_layer.listeners.append(cur_layer)
        #     self.layers.append(cur_layer)
        #     prev_layer = cur_layer
        # self.output_layer = self[-1]
        #
        # # add context layer
        # context_layer = ContextLayer(shape[1], self[1].neurons)
        # self[1].listeners.append(context_layer)
        # self[1].add_input(context_layer.neurons)


    def __len__(self):
        return len(self.shape)

    def __getitem__(self, i):
        return self.layers[i]

    def calculate(self, x, random_value=None):
        self.input_layer.calculate(x)
        self.input_layer.notify_listeners()
        if random_value:
            for neuron in self.output_layer:
                neuron.out += (random.random()*2-1)*random_value
        return self.output_layer.get_output_values()

    def teach_considering_random(self, promotion_value):
        answer_with_random = self.output_layer.get_output_values()
        answer_without_random = self.calculate(self.input_layer.input_values)
        if promotion_value < 0:
            answer_with_random = [-x for x in answer_with_random]
            promotion_value = -promotion_value
        self.output_layer.teach_output_layer2(promotion_value, answer_with_random)

        # teach middle layers
        self.middle_layer.teach_middle_layer(promotion_value)

        for layer in self:
            layer.commit_teach()

    def teach(self, error_value):
        self.output_layer.teach_output_layer(self.learn_rate, error_value)
        self.middle_layer.teach_middle_layer(self.learn_rate)
        for layer in self:
            layer.commit_teach()

    def teach2(self, database):
        error_value = 0
        for d in database:
            y = self.calculate(d[0])
            self.time += 1

            # teach last layer
            self.output_layer.teach_output_layer2(self.learn_rate, d[1])

            # teach middle layers
            for li in range(len(self) - 2, 0, -1):
                self[li].teach_middle_layer(self.learn_rate)

            for layer in self:
                layer.commit_teach()

            error_value += sum([math.pow(y[i] - d[1][i], 2) for i in range(len(y))])

        return error_value / float(len(database))

    def teach_elman(self, database, clear_context=True):
        error_value = 0
        for d in database:
            for inp in d[0]:
                y = self.calculate(inp)

            self.time += 1

            # teach last layer
            self.output_layer.teach_output_layer(self.learn_rate, d[1])

            # teach middle layers
            self.middle_layer.teach_middle_layer(self.learn_rate)

            for layer in self:
                layer.commit_teach()

            if clear_context:
                self.clean_context()

            error_value += sum([math.pow(y[i] - d[1][i], 2) for i in range(len(y))])

        return error_value / float(len(database))

    def clean_context(self):
        self.context_layer.clean()