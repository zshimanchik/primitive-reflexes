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
        return self.random_layer.get_output_values()

    def teach_considering_random(self, stimulation_value):
        """
        teach network with learn_rate = abs(stimulation_value). calculate with random value should be used before
        using this method.
        if stimulation_value > 0 then network teaches like usual by example, which is equals previous calculation result
        if stimulation_value < 0: then example vector is opposite previous calculation result.
        For correct teaching, method recalculate input values=self.input_layer.input_values, without random.
        :param stimulation_value:
        """
        answer_with_random = self.random_layer.get_output_values()
        if stimulation_value < 0:
            answer_with_random = [-x for x in answer_with_random]
            stimulation_value = -stimulation_value
        self.output_layer.teach_output_layer_by_sample(stimulation_value, answer_with_random)

        # teach middle layers
        self.middle_layer.teach_middle_layer(stimulation_value)

        for layer in self:
            layer.commit_teach()