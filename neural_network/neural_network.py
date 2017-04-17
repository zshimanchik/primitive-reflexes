import math
import tensorflow as tf


class NeuralNetwork:
    def __init__(self, shape, log_dir='tf_log'):
        assert len(shape) == 3  # todo it flexible
        self._log = bool(log_dir)  # todo do not log if log_dir is not set

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

        self.summary_writer = tf.summary.FileWriter(log_dir, graph=self.session.graph)

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

    def train(self, teach_inputs, teach_targets, count=500):
        feed_dict = {
            self.input: teach_inputs,
            self.teach_values: teach_targets,
        }
        for _ in range(count):
            self.session.run(self.train_step, feed_dict)
