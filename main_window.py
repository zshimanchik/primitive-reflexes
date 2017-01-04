__author__ = 'zshimanchik'
import sys
import math
import random
from collections import deque
from itertools import zip_longest

from PyQt4.QtGui import QBrush, QColor
from PyQt4 import QtGui, QtCore

from world import World, BLUE, GREEN
from primitive import Primitive
from NeuralNetworkViewer import NeuralNetworkViewer
from neural_network_viewer import NeuralNetworkViewer as NNV2


class MainWindow(QtGui.QWidget):
    PLOT_ZOOM = 800

    def __init__(self, primitive, nnv_window):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Main Windows")
        self.resize(400, 400)
        self.mouse = Mouse()
        self.world = World(self.width(), self.height(), self.mouse)
        self.nnv_window = nnv_window
        self.nnv = None

        width = self.width()
        self.stimulation_func = deque(maxlen=width)
        self.state_func = deque(maxlen=width)
        self.brain_stimulation_func = deque(maxlen=width)
        self.need_to_draw_plots = False

        self.timer_interval = 1
        self.timer = QtCore.QBasicTimer()
        self.timer.start(self.timer_interval, self)
        self.auto_teach = False
        self.auto_teach_counter = 0

    def timerEvent(self, event):
        self.setWindowTitle("{:.4f} : {:.6f} : {:.6f}"
                            .format(self.world.prim.state, self.world.prim.stimulation, self.world.prim.brain_stimulation))
        if self.need_to_draw_plots:
            self._append_plot_info()

        self.world.update()

        self.repaint()
        self.nnv_window.repaint()
        if self.nnv:
            self.nnv.repaint()
        if self.auto_teach:
            self._update_auto_teach()

    def _append_plot_info(self):
        self.state_func.append(self.world.prim.state)
        self.stimulation_func.append(self.world.prim.stimulation)
        self.brain_stimulation_func.append(self.world.prim.brain_stimulation)

    def _update_auto_teach(self):
        self.auto_teach_counter -= 1
        if self.auto_teach_counter <= 0:
            self.auto_teach_counter = random.randint(500, 1000)
            but = random.randint(0, 0)
            self.mouse.but1_pressed = but == 0
            self.mouse.but2_pressed = but == 1
            self.mouse.but3_pressed = but == 2
            self.mouse.x = random.randint(0, self.width())
            self.mouse.y = random.randint(0, self.height())
            self.mouse.area_size = random.randint(100, 400)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        self._draw_debug_text(painter)

        if self.need_to_draw_plots:
            self._draw_plots(painter)

        self._draw_primitive(painter)
        self._draw_sensors(painter)

        if self.mouse.pressed():
            self.mouse.draw(painter)

        painter.end()

    def _draw_debug_text(self, painter):
        args = [iter(self.world.prim.sensor_values)] * 3
        sensor_iter = zip_longest(*args, fillvalue=0)
        painter.drawText(
            QtCore.QRect(0, 0, 200, 150),
            QtCore.Qt.AlignTop,
            '\n'.join("{:.4f}, {:.4f}, {:.4f}".format(*x) for x in sensor_iter)
        )
        painter.drawText(
            QtCore.QRect(200, 0, 100, 50),
            QtCore.Qt.AlignTop,
            '{:.6f}\n{:.6f}'.format(self.world.get_influence_value(), self.world.prim.stimulation)
        )

    def _draw_plots(self, painter):
        painter.setPen(QtCore.Qt.gray)
        painter.drawLine(0, 200, len(self.stimulation_func), 200)
        painter.setPen(QtCore.Qt.darkCyan)
        for i in range(len(self.state_func) - 1):
            painter.drawLine(i, -self.state_func[i] * 70 + 200, i + 1, -self.state_func[i + 1] * 70 + 200)
        painter.setPen(QtCore.Qt.red)
        for i in range(len(self.stimulation_func) - 1):
            painter.drawLine(i, -self.stimulation_func[i] * self.PLOT_ZOOM + 200,
                             i + 1, -self.stimulation_func[i + 1] * self.PLOT_ZOOM + 200)
        painter.setPen(QtCore.Qt.darkBlue)
        for i in range(len(self.brain_stimulation_func) - 1):
            painter.drawLine(i, -self.brain_stimulation_func[i] * self.PLOT_ZOOM + 200,
                             i + 1, -self.brain_stimulation_func[i + 1] * self.PLOT_ZOOM + 200)

    def _draw_primitive(self, painter):
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(brush(170, 170, 170))
        painter.drawEllipse(self.world.prim.x - self.world.prim.size,
                            self.world.prim.y - self.world.prim.size,
                            self.world.prim.size * 2,
                            self.world.prim.size * 2)
        painter.drawLine(self.world.prim.x,
                         self.world.prim.y,
                         self.world.prim.x + math.cos(self.world.prim.angle) * self.world.prim.size,
                         self.world.prim.y + math.sin(self.world.prim.angle) * self.world.prim.size)

    def _draw_sensors(self, painter):
        painter.setBrush(brush(0, 0, 0))
        for i, sensor_pos in enumerate(self.world.prim.sensors_positions()):
            sensor_value = self.world.prim.sensor_values[i*3:(i+1)*3]
            painter.setBrush(brush_f(sensor_value))
            painter.drawEllipse(sensor_pos[0] - 3, sensor_pos[1] - 3, 6, 6)

    def mousePressEvent(self, event):
        self.mouse.fixed = False
        self.mouse.x = event.x()
        self.mouse.y = event.y()

        self.mouse.but1_pressed = False
        self.mouse.but2_pressed = False
        self.mouse.but3_pressed = False

        if event.button() == 1:
            self.mouse.but1_pressed = True
        elif event.button() == 2:
            self.mouse.but2_pressed = True
        elif event.button() == 4:
            self.mouse.but3_pressed = True

    def mouseReleaseEvent(self, event):
        if not self.mouse.fixed:
            self.mouse.x = event.x()
            self.mouse.y = event.y()
            if event.button() == 1:
                self.mouse.but1_pressed = False
            elif event.button() == 2:
                self.mouse.but2_pressed = False
            elif event.button() == 4:
                self.mouse.but3_pressed = False

    def wheelEvent(self, event):
        self.mouse.area_size += event.delta()/120

    def mouseMoveEvent(self, event):
        if not self.mouse.fixed:
            self.mouse.x = event.x()
            self.mouse.y = event.y()
            if self.mouse.pressed():
                self.repaint()

    def keyPressEvent(self, event):
        if Primitive.DEBUG:
            print("key={} ".format(event.key()))
        if event.key() == 32:  # space
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start(self.timer_interval, self)
        elif event.key() == 67:  # c
            self.need_to_draw_plots = not self.need_to_draw_plots
        elif event.key() == 43:  # -
            if self.timer_interval < 20:
                self.set_timer_interval(self.timer_interval - 1)
            else:
                self.set_timer_interval(self.timer_interval - 20)
        elif event.key() == 45:  # +
            if self.timer_interval < 20:
                self.set_timer_interval(self.timer_interval + 1)
            else:
                self.set_timer_interval(self.timer_interval + 20)
        elif event.key() == 16777219:  # backspace
            self.set_timer_interval(1)
        elif event.key() == 88:  # x
            self.world.prim.brain.context_layer.clean()
            if Primitive.DEBUG:
                print("context cleared")
        elif event.key() == 70:  # f
            self.mouse.fixed = not self.mouse.fixed
        elif event.key() == 65:  # a
            self.auto_teach = not self.auto_teach
            if Primitive.DEBUG:
                print("auto teach = {}".format(self.auto_teach))
        elif event.key() == 68: # d
            Primitive.DEBUG = not Primitive.DEBUG
        elif event.key() == 78:  # n
            self.nnv_window.setVisible(not self.nnv_window.isVisible())
            self.nnv = NeuralNetworkViewer(self.world.prim.brain)
            self.nnv.setVisible(True)

    def set_timer_interval(self, interval):
        self.timer_interval = max(1, interval)
        self.timer.stop()
        self.timer.start(self.timer_interval, self)

    def resizeEvent(self, event):
        width = self.width()
        self.world.width = width
        self.world.height = self.height()
        self.stimulation_func = deque(self.stimulation_func, maxlen=width)
        self.state_func = deque(self.state_func, maxlen=width)
        self.brain_stimulation_func = deque(self.brain_stimulation_func, maxlen=width)

    def closeEvent(self, event):
        self.nnv_window.close()
        self.nnv.close()


class Mouse(object):
    GREEN_AREA_RATIO = 0.5

    def __init__(self):
        self.x, self.y = 0, 0
        self.fixed = False
        self.but1_pressed = False
        self.but2_pressed = False
        self.but3_pressed = False
        self.but1_brush = brush(80, 180, 60, alpha=100)
        self.but2_brush = brush(180, 60, 80, alpha=100)
        self.but3_brush = brush(60, 80, 180, alpha=100)
        self._area_size = 10
        self._influence_area_size = self._area_size * self.GREEN_AREA_RATIO

    @property
    def area_size(self):
        return self._area_size

    @area_size.setter
    def area_size(self, value):
        self._area_size = value
        self._influence_area_size = self._area_size * self.GREEN_AREA_RATIO

    @property
    def influence_area_size(self):
        if self.but3_pressed:
            return self._influence_area_size
        else:
            return self._area_size

    def pressed(self):
        return self.but1_pressed or self.but2_pressed or self.but3_pressed

    def draw(self, qp):
        old_brush = qp.brush()
        self.but1_pressed and qp.setBrush(self.but1_brush)
        self.but2_pressed and qp.setBrush(self.but2_brush)
        self.but3_pressed and qp.setBrush(self.but3_brush)
        qp.drawEllipse(self.x - self.area_size,
                       self.y - self.area_size,
                       self.area_size * 2,
                       self.area_size * 2)
        qp.setBrush(old_brush)


def brush(r, g, b, alpha=255):
    return QBrush(QColor(r, g, b, alpha))


def brush_f(color):
    if BLUE == color:
        return QBrush(QColor(66,170,255))
    elif GREEN == color:
        return QBrush(QColor(0,255,0))
    return QBrush(QColor(color[0]*255, color[1]*255, color[2]*255))


def main():
    application = QtGui.QApplication(sys.argv)
    primitive = Primitive()
    nnv_window = NeuralNetworkViewer(primitive.brain)
    nnv_window = NNV2(network=primitive.brain)
    window = MainWindow(primitive, nnv_window)
    window.show()
    # nnv_window.show()
    sys.exit(application.exec_())


if __name__ == '__main__':
    main()