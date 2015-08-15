from Layer import Layer, InputLayer, RandomLayer


class NeuralNetwork:
    def __init__(self, shape, random_value):
        self.layers = []
        self.shape = shape
        self.time = 0

        self.input_layer = InputLayer(shape[0])

        self.middle_layer = Layer(shape[1], self.input_layer.neurons)
        self.input_layer.listeners.append(self.middle_layer)

        self.output_layer = Layer(shape[2], self.middle_layer.neurons)
        self.middle_layer.listeners.append(self.output_layer)

        self.random_layer = RandomLayer(shape[2], self.output_layer.neurons, random_value)
        self.output_layer.listeners.append(self.random_layer)

        self.layers.append(self.input_layer)
        self.layers.append(self.middle_layer)
        self.layers.append(self.output_layer)
        self.layers.append(self.random_layer)

        self.max_history_length = 20
        self.history = [([0] * shape[0], [0]*shape[2])] * self.max_history_length

    def __len__(self):
        return len(self.shape)

    def __getitem__(self, i):
        return self.layers[i]

    def calculate(self, x):
        """
        calculate vector x, if random value is set, add to result vector value (random()*2-1)*random_value
        :param x: input vector
        :param random_value: random range added to result vector
        :return: result of network calculation
        """
        self.input_layer.calculate(x)
        self.input_layer.notify_listeners()
        self.history.pop(-1)
        self.history.insert(0, (x, self.random_layer.get_output_values()))
        return self.random_layer.get_output_values()

    def _teach(self, stimulation_value, input=None, output=None):
        if input is not None:
            self.input_layer.calculate(input)
            self.input_layer.notify_listeners()
        else:
            output = self.random_layer.get_output_values()

        if stimulation_value < 0:
            output = [-x for x in output]
            stimulation_value = -stimulation_value

        self.output_layer.teach_output_layer_by_sample(stimulation_value, output)

        # teach middle layers
        self.middle_layer.teach_middle_layer(stimulation_value)

        for layer in self:
            layer.commit_teach()


    def teach(self, stimulation_value):
        """
        teach network with learn_rate = abs(stimulation_value).
        if stimulation_value > 0 then network teaches like usual by example, which is equals previous calculation result
        if stimulation_value < 0: then example vector is opposite previous calculation result.
        :param stimulation_value:
        """
        for input, output in self.history:
            self._teach(stimulation_value, input, output)
            stimulation_value /= 5.0