__author__ = 'arch'
from NeuralNetwork import *

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QRect
from PyQt4.QtGui import QBrush, QPen, QColor
import math
from random import randint

def brush(r, g, b, alpha=255):
    return QBrush(QColor(r, g, b, alpha))
def pen(r, g, b, alpha=255):
    return QPen(QColor(r, g, b, alpha))

def setColor(qp, color):
    color = max(0, min(255, color))
    qp.setBrush(brush(100, color, 255-color))
    qp.setPen(pen(100, color, 255-color))


class NeuralNetworkViewer(QtGui.QWidget):
    def __init__(self, network):
        super(NeuralNetworkViewer, self).__init__()
        self.setWindowTitle("NeuralNetwork viewer")
        self.resize(400, 400)
        self.network = network
        print len(network)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        cell_width = self.width()
        cell_height = self.height()/len(self.network)

        self.draw_layer(qp, self.network.input_layer, 0, 0, cell_width, cell_height)
        # self.draw_layer(qp, self.network.context_layer, cell_width/2, 0, cell_width/2, cell_height)

        self.draw_layer(qp, self.network.middle_layer, 0, 1*cell_height, cell_width, cell_height, draw_w=True)
        self.draw_layer(qp, self.network.output_layer, 0, 2*cell_height, cell_width, cell_height, draw_w=True)

        qp.end()

    def draw_layer(self, qp, layer, x, y, width, height, draw_w=False):
        qp.setBrush(brush(randint(0,255), randint(0,255), randint(0,255)))
        # qp.drawRect(x, y, width, height)
        cell_height = height*0.7
        cell_width = width / len(layer)
        y += height * 0.15

        for i in range(len(layer)):
            neuron = layer[i]
            rect = QRect(x+i*cell_width, y, cell_width, cell_height)

            if draw_w:
                # draw w0
                setColor(qp, int((neuron.w0+1)*255/2.0))
                qp.drawPie(rect, 0, -180*16)
                # draw out
                setColor(qp, int((neuron.out+1)*255/2.0))
                qp.drawChord(rect, -20*16, -140*16)
                # draw w
                w_angle = 180 * 16 / float(len(neuron.w))
                for j in range(len(neuron.w)):
                    setColor(qp, int((neuron.w[j]+1)*255/2.0))
                    qp.drawPie(rect, j*w_angle, w_angle)
            else:
                # draw out
                setColor(qp, int((neuron.out+1)*255/2.0))
                qp.drawPie(rect, 0, -180*16)
                # draw input
                setColor(qp, int((layer.input_values[i]+1) * 255.0 / 2.0))
                qp.drawPie(rect, 0, 180*16)



if __name__ == "__main__":
    pass