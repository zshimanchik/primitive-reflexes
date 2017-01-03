from __future__ import division

from PyQt4 import QtGui
from PyQt4.QtCore import QRect, Qt
from PyQt4.QtGui import QPen, QBrush, QColor


def get_color(color):
    r, g, b = max(0, -color), max(0, color), 0
    return QColor(r * 255, g * 255, b * 255)


class NeuralNetworkViewer(QtGui.QMainWindow):
    def __init__(self, network=None, parent=None):
        super(NeuralNetworkViewer, self).__init__()
        self.network = network

        self.central_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("NeuralNetwork viewer")
        self.resize(700, 300)

    def paintEvent(self, event):
        if self.network:
            qp = QtGui.QPainter()
            qp.begin(self)
            self.draw_animal_brain(qp, self.network)
            qp.end()

    def draw_layer(self, qp, layer, x, y, width, height):
        cell_height = height*0.7
        cell_width = width / len(layer)
        y += height * 0.15

        qp.setPen(Qt.NoPen)
        for i, neuron in enumerate(layer):
            rect = QRect(x+i*cell_width, y, cell_width, cell_height)
            qp.setBrush(QBrush(get_color(neuron.out)))
            qp.drawEllipse(rect)

    def draw_animal_brain(self, painter, brain):
        width_count = max([len(layer) for layer in brain])
        neuron_size = min(self.width() / (width_count * 1.5), self.height() / (len(brain) * 2.0))


        for i in range(len(brain) - 1):
            self.draw_layers_connections(painter, brain, i, i + 1, neuron_size)

        for layer_index, layer in enumerate(brain):
            neuron_margin = (self.width() - len(layer) * neuron_size) / (len(layer) + 1)
            for neuron_index, neuron in enumerate(layer):
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(get_color(neuron.out)))

                rect = QRect(
                    neuron_index * (neuron_size + neuron_margin) + neuron_margin,
                    layer_index * neuron_size * 2,
                    neuron_size,
                    neuron_size
                )
                painter.drawEllipse(rect)

                if neuron.out > 0:
                    painter.setPen(QPen(QColor(255, 0, 0)))
                else:
                    painter.setPen(QPen(QColor(0, 255, 0)))
                painter.drawText(rect, Qt.AlignCenter, "{:+.3f}".format(neuron.out))


    def draw_layers_connections(self, painter, brain, first_layer_index, second_layer_index, neuron_size):
        first_layer_margin = \
                (self.width() - len(brain[first_layer_index]) * neuron_size) / (len(brain[first_layer_index]) + 1)
        second_layer_margin = \
                (self.width() - len(brain[second_layer_index]) * neuron_size) / (len(brain[second_layer_index]) + 1)
        for second_layer_neuron_index, second_layer_neuron in enumerate(brain[second_layer_index]):
            for first_layer_neuron_index, first_layer_neuron in enumerate(brain[first_layer_index]):
                if not len(second_layer_neuron.w):
                    continue
                # color = get_color(second_layer_neuron.w[first_layer_neuron_index])
                if second_layer_neuron.w[first_layer_neuron_index] < 0:
                    color = QColor(200, 50, 50)
                else:
                    color = QColor(50, 200, 50)

                width = min(6, abs(second_layer_neuron.w[first_layer_neuron_index]) * 6) + 1
                painter.setPen(QPen(color, width))

                x1 = second_layer_margin + second_layer_neuron_index * (neuron_size + second_layer_margin) \
                    + neuron_size / 2.0
                y1 = second_layer_index * neuron_size * 2.0 + neuron_size / 2.0
                x2 = first_layer_margin + first_layer_neuron_index * (neuron_size + first_layer_margin) \
                    + neuron_size / 2.0
                y2 = first_layer_index * neuron_size * 2.0 + neuron_size / 2.0

                painter.drawLine(x1, y1, x2, y2)


if __name__ == "__main__":
    pass
