__author__ = 'zshimanchik'
import sys
import math
import random

from PyQt4.QtGui import QBrush, QColor
from PyQt4 import QtGui, QtCore

from Primitive import Primitive
from NeuralNetworkViewer import NeuralNetworkViewer


def brush(r, g, b, alpha=255):
    return QBrush(QColor(r, g, b, alpha))


class MainWindow(QtGui.QWidget):
    INTERSECT_VALUE_TO_INFLUENCE_VALUE_RATIO = 1 / 200.0
    PLOT_ZOOM = 800

    GREEN_AREA_RATIO = 0.5
    BLACK = (0.0, 0.0, 0.0)
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 0.0)

    def __init__(self, primitive, nnv_window):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Main Windows")
        self.resize(400, 400)
        self.mouse = Mouse()
        self.prim = primitive
        self.nnv_window = nnv_window

        self.stimulation_func = PlotFunction(self.width(), shifted=True)
        self.state_func = PlotFunction(self.width(), shifted=True)
        self.brain_stimulation_func = PlotFunction(self.width(), shifted=True)
        self.draw_plots = False

        self.timer_interval = 300
        self.timer = QtCore.QBasicTimer()
        self.timer.start(self.timer_interval, self)
        self.auto_teach = False
        self.auto_teach_counter = 0

    def timerEvent(self, event):
        self.setWindowTitle("{:.4f} : {:.6f} : {:.6f}"
                            .format(self.prim.state, self.prim.stimulation, self.prim.brain_stimulation))
        self.update_primitive_position()
        if self.draw_plots:
            self.state_func.add_value(self.prim.state)
            self.stimulation_func.add_value(self.prim.stimulation)
            self.brain_stimulation_func.add_value(self.prim.brain_stimulation)

        influence_value = self.get_influence_value()
        self.prim.change_state(influence_value)
        sensors_values = []
        map(sensors_values.extend, (self.get_sensor_value(x, y) for x, y in self.prim.sensors_positions()))
        self.prim.update(sensors_values)

        self.repaint()
        self.nnv_window.repaint()
        if self.auto_teach:
            self.auto_teach_counter -= 1
            if self.auto_teach_counter <= 0:
                self.auto_teach_counter = random.randint(500, 1000)
                self.mouse.but1_pressed = random.randint(0, 1) == 0
                self.mouse.but2_pressed = not self.mouse.but1_pressed
                self.mouse.x = random.randint(0, self.width())
                self.mouse.y = random.randint(0, self.height())
                self.mouse.area_size = random.randint(10, 40)

    def get_sensor_value(self, x, y):
        distance = math.sqrt((self.mouse.x - x) ** 2 + (self.mouse.y - y) ** 2)
        if self.mouse.pressed() and distance < self.mouse.area_size:
            if self.mouse.but1_pressed:
                return MainWindow.GREEN
            elif self.mouse.but2_pressed:
                return MainWindow.RED
            elif self.mouse.but3_pressed:
                if distance < self.mouse.influence_area_size:
                    return MainWindow.GREEN
                else:
                    return MainWindow.BLUE
        return MainWindow.BLACK

    def get_influence_value(self):
        val = 0
        if self.mouse.pressed():
            val = self.calc_intersect_value() * MainWindow.INTERSECT_VALUE_TO_INFLUENCE_VALUE_RATIO
            if self.mouse.but2_pressed:
                val *= -1
        return val

    def calc_intersect_value(self):
        dist = math.sqrt((self.mouse.x - self.prim.x) ** 2 + (self.mouse.y - self.prim.y) ** 2)
        intersect_length = max(0, self.mouse.influence_area_size + self.prim.size - dist)
        intersect_length = min(intersect_length, self.mouse.influence_area_size * 2, self.prim.size * 2)
        return (intersect_length ** 2) / 2

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)

        # drawing plots
        if self.draw_plots:
            qp.setPen(QtCore.Qt.gray)
            qp.drawLine(0, 200, len(self.stimulation_func), 200)
            qp.setPen(QtCore.Qt.darkCyan)
            for i in range(len(self.state_func) - 1):
                qp.drawLine(i, -self.state_func[i] * 70 + 200, i + 1, -self.state_func[i + 1] * 70 + 200)
            qp.setPen(QtCore.Qt.red)
            for i in range(len(self.stimulation_func) - 1):
                qp.drawLine(i, -self.stimulation_func[i] * MainWindow.PLOT_ZOOM + 200,
                            i + 1, -self.stimulation_func[i + 1] * MainWindow.PLOT_ZOOM + 200)
            qp.setPen(QtCore.Qt.darkBlue)
            for i in range(len(self.brain_stimulation_func) - 1):
                qp.drawLine(i, -self.brain_stimulation_func[i] * MainWindow.PLOT_ZOOM + 200,
                            i + 1, -self.brain_stimulation_func[i + 1] * MainWindow.PLOT_ZOOM + 200)

        # drawing primitive
        qp.setPen(QtCore.Qt.black)
        qp.setBrush(brush(170, 170, 170))
        qp.drawEllipse(self.prim.x - self.prim.size,
                       self.prim.y - self.prim.size,
                       self.prim.size * 2,
                       self.prim.size * 2)
        # drawing sensors
        qp.setBrush(brush(0, 0, 0))
        for sensor_pos in self.prim.sensors_positions():
            qp.drawEllipse(sensor_pos[0] - 3, sensor_pos[1] - 3, 6, 6)
        # drawing mouse
        if self.mouse.pressed():
            self.mouse.draw(qp)

        qp.end()

    def update_primitive_position(self):
        if self.prim.x < 0:
            self.prim.x = self.width() - 10
        if self.prim.x > self.width():
            self.prim.x = 10

        if self.prim.y < 0:
            self.prim.y = self.height() - 10
        if self.prim.y > self.height():
            self.prim.y = 10

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
            self.draw_plots = not self.draw_plots
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
            self.prim.brain.context_layer.clean()
            if Primitive.DEBUG:
                print("context cleared")
        elif event.key() == 70:  # f
            self.mouse.fixed = not self.mouse.fixed
        elif event.key() == 65:  # a
            self.auto_teach = not self.auto_teach
            if Primitive.DEBUG:
                print("auto teach = {}".format(self.auto_teach))
        elif event.key() == 78:  # n
            self.nnv_window.setVisible(not self.nnv_window.isVisible())

    def set_timer_interval(self, interval):
        self.timer_interval = max(1, interval)
        self.timer.stop()
        self.timer.start(self.timer_interval, self)

    def resizeEvent(self, event):
        self.stimulation_func.set_size(self.width())
        self.state_func.set_size(self.width())
        self.brain_stimulation_func.set_size(self.width())

    def closeEvent(self, event):
        self.nnv_window.close()


class Mouse(object):
    def __init__(self):
        self.x, self.y = 0, 0
        self.fixed = False
        self.but1_pressed = False
        self.but2_pressed = False
        self.but3_pressed = False
        self.but1_brush = brush(80, 180, 60, alpha=175)
        self.but2_brush = brush(180, 60, 80, alpha=175)
        self.but3_brush = brush(60, 80, 180, alpha=175)
        self._area_size = 10
        self._influence_area_size = self._area_size * MainWindow.GREEN_AREA_RATIO

    @property
    def area_size(self):
        return self._area_size

    @area_size.setter
    def area_size(self, value):
        self._area_size = value
        self._influence_area_size = self._area_size * MainWindow.GREEN_AREA_RATIO

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
        if self.but3_pressed:
            qp.setBrush(self.but1_brush)
            qp.drawEllipse(self.x - self.influence_area_size,
                           self.y - self.influence_area_size,
                           self.influence_area_size * 2,
                           self.influence_area_size * 2)
        qp.setBrush(old_brush)


class PlotFunction():
    def __init__(self, size, shifted=False):
        self.size = size
        self.values = [0] * self.size
        self.last_value = 0
        self.shifted = shifted

    def set_size(self, new_size):
        self.size = new_size
        self.values = [0] * self.size
        self.last_value = 0

    def add_value(self, value):
        self.last_value += 1
        if self.last_value >= self.size:
            self.last_value = 0
        self.values[self.last_value] = value

    def __getitem__(self, i):
        return self.values[(i + (self.last_value + 1) * self.shifted) % self.size]

    def __len__(self):
        return self.size


def main():
    application = QtGui.QApplication(sys.argv)
    primitive = Primitive()
    nnv_window = NeuralNetworkViewer(primitive.brain)
    window = MainWindow(primitive, nnv_window)
    window.show()
    # nnv_window.show()
    sys.exit(application.exec_())


if __name__ == '__main__':
    main()