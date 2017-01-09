import math
import tensorflow as tf


class NeuralNetwork:
    def __init__(self, shape, summary_file='tf_log'):
        assert len(shape) == 3  # todo it flexible
        self._log = bool(summary_file)
        self.last_input = []
        self.last_output_with_random = []
        self.i = 0

        self.input = tf.placeholder(tf.float32, [None, shape[0]])
        self.teach_values = tf.placeholder(tf.float32, [None, shape[-1]])
        self.learning_rate = tf.Variable(initial_value=0.1, trainable=False, name='learning_rate')

        self._init_layers(shape)

        self.loss = tf.reduce_mean(tf.squared_difference(self.output, self.teach_values))
        self.train_step = tf.train.GradientDescentOptimizer(0.035).minimize(self.loss)
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('learning_rate', self.learning_rate)
        self.summaries = tf.summary.merge_all()
        self.session = tf.InteractiveSession()
        tf.global_variables_initializer().run()

        self.summary_writer = tf.summary.FileWriter(summary_file, graph=self.session.graph)

    def _init_layers(self, shape):
        with tf.name_scope('hidden1'):
            weights = tf.Variable(
                tf.truncated_normal(
                    [shape[0], shape[1]],
                    stddev=1.0 / math.sqrt(float(shape[0]))
                ),
                name='weights'
            )
            biases = tf.Variable(tf.zeros([shape[1]]))
            hidden1 = tf.nn.relu(tf.matmul(self.input, weights) + biases)

        with tf.name_scope('output'):
            weights = tf.Variable(
                tf.truncated_normal(
                    [shape[1], shape[2]],
                    stddev=1.0 / math.sqrt(float(shape[1]))
                ),
                name='weights'
            )
            biases = tf.Variable(tf.zeros([shape[2]]))
            self.output = tf.nn.relu(tf.matmul(hidden1, weights) + biases)

    def calculate(self, x):
        res = self.session.run(self.output, feed_dict={self.input: x})
        return res

    def train(self, teach_inputs, teach_targets):
        feed_dict = {
            self.input: teach_inputs,
            self.teach_values: teach_targets,
        }
        for _ in range(500):
            self.session.run(self.train_step, feed_dict)

    def teach_considering_random(self, stimulation_value):
        """
        teach network with learn_rate = abs(stimulation_value). calculate with random value should be used before
        using this method.
        if stimulation_value > 0 then network teaches like usual by example, which is equals previous calculation result
        if stimulation_value < 0: then example vector is opposite previous calculation result.
        :param stimulation_value:
        """
        pass
        # self.i += 1
        # if stimulation_value < 0:
        #     answer_with_random = [-x for x in self.last_output_with_random]
        #     stimulation_value = -stimulation_value
        # else:
        #     answer_with_random = self.last_output_with_random
        #
        # feed_dict = {
        #     self.input: self.last_input,
        #     self.teach_values: [answer_with_random],
        #     self.learning_rate: stimulation_value,
        # }
        #
        # if self._log:
        #     (_, summary) = self.session.run([self.train_step, self.summaries], feed_dict)
        #     self.summary_writer.add_summary(summary, self.i)
        # else:
        #     self.session.run(self.train_step, feed_dict)



