__author__ = 'zshimanchik'
import sys
import math
import random
import time
from multiprocessing import Pool

from PyQt4.QtGui import QBrush, QColor
from PyQt4 import QtGui, QtCore

from Primitive import Primitive
from NeuralNetworkViewer import NeuralNetworkViewer
from IntersectCalculation import calc_triangle_and_circle_intersect_2

pool = Pool(3)


def brush(r, g, b, alpha=255):
    return QBrush(QColor(r, g, b, alpha))


class MainWindow(QtGui.QWidget):
    INTERSECT_VALUE_TO_INFLUENCE_VALUE_RATIO = 1 / 200.0
    PLOT_ZOOM = 800

    def __init__(self, primitive, nnv_window):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Main Windows")
        self.resize(400, 400)
        self.mouse = Mouse()
        self.prim = primitive
        self.nnv_window = nnv_window

        self.stimulation_func = PlotFunction(self.width(), shifted=True)
        self.brain_stimulation_func = PlotFunction(self.width(), shifted=True)
        self.draw_plots = False

        self.timer_interval = 300
        self.timer = QtCore.QBasicTimer()
        self.timer.start(self.timer_interval, self)
        self.auto_teach = False
        self.auto_teach_counter = 0

        self.fps_prev_time = time.time()

    def timerEvent(self, event):
        now = time.time()
        self.setWindowTitle("fps={}".format(now - self.fps_prev_time))
        self.fps_prev_time = now

        self.update_primitive_position()
        if self.draw_plots:
            self.stimulation_func.add_value(self.prim.stimulation)
            self.brain_stimulation_func.add_value(self.prim.brain_stimulation)

        influence_value = self.get_influence_value()
        self.prim.change_state(influence_value)
        sensors_values = [self.get_sensor_value(x, y) for x, y in self.prim.sensors]
        self.prim.update(sensors_values)

        self.update()
        self.nnv_window.update()

        if self.auto_teach:
            self.auto_teach_counter -= 1
            if self.auto_teach_counter <= 0:
                self.auto_teach_counter = random.randint(500, 1000)
                self.mouse.but1_pressed = random.randint(0, 1) == 0
                self.mouse.but2_pressed = not self.mouse.but1_pressed
                self.mouse.x = random.randint(0, self.width())
                self.mouse.y = random.randint(0, self.height())
                self.mouse.area_size = random.randint(20, 60)

    def get_sensor_value(self, x, y):
        if self.mouse.pressed() and math.sqrt((self.mouse.x - x) ** 2 + (self.mouse.y - y) ** 2) < self.mouse.area_size:
            if self.mouse.but1_pressed:
                return 1.0
            elif self.mouse.but2_pressed:
                return -1.0
        return 0.0

    def get_influence_value(self):
        val = 0
        if self.mouse.but1_pressed or self.mouse.but2_pressed:
            val = self.calc_intersect_value() * MainWindow.INTERSECT_VALUE_TO_INFLUENCE_VALUE_RATIO
            if self.mouse.but2_pressed:
                val *= -1
        return val

    def triangles_generator(self):
        for i in range(-1, len(self.prim.sensors) - 1):
            yield (self.prim.middle_x, self.prim.middle_y), self.prim.sensors[i], self.prim.sensors[i + 1], \
                  (self.mouse.x, self.mouse.y), self.mouse.area_size

    def calc_intersect_value(self):
        return sum(pool.map(calc_triangle_and_circle_intersect_2, self.triangles_generator()))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)

        # drawing plots
        if self.draw_plots:
            qp.setPen(QtCore.Qt.gray)
            qp.drawLine(0, 200, len(self.stimulation_func), 200)
            qp.setPen(QtCore.Qt.darkBlue)
            for i in range(len(self.brain_stimulation_func) - 1):
                qp.drawLine(i, -self.brain_stimulation_func[i] * MainWindow.PLOT_ZOOM + 200,
                            i + 1, -self.brain_stimulation_func[i + 1] * MainWindow.PLOT_ZOOM + 200)
            qp.setPen(QtCore.Qt.red)
            for i in range(len(self.stimulation_func) - 1):
                qp.drawLine(i, -self.stimulation_func[i] * MainWindow.PLOT_ZOOM + 200,
                            i + 1, -self.stimulation_func[i + 1] * MainWindow.PLOT_ZOOM + 200)
        # drawing primitive
        qp.setPen(QtCore.Qt.black)
        qp.setBrush(brush(170, 170, 170))
        qp.drawPolygon(*[QtCore.QPoint(*sensor) for sensor in self.prim.sensors])
        # drawing sensors
        color = 0
        for sensor in self.prim.sensors:
            qp.setBrush(brush(color, color, color))
            qp.drawEllipse(sensor[0] - 3, sensor[1] - 3, 6, 6)
            color += 255 / len(self.prim.sensors)
        qp.setBrush(brush(255, 0, 0))
        qp.drawEllipse(self.prim.middle_x - 3, self.prim.middle_y - 3, 6, 6)
        # drawing mouse
        if self.mouse.pressed():
            self.mouse.draw(qp)

        qp.end()

    def update_primitive_position(self):
        if self.prim.middle_x < 0 or self.prim.middle_x > self.width() or self.prim.middle_y < 0 or self.prim.middle_y > self.height():
            dx = self.width() / 2 - self.prim.middle_x
            dy = self.height() / 2 - self.prim.middle_y
            for sensor in self.prim.sensors:
                sensor[0] += dx
                sensor[1] += dy

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
        self.mouse.area_size += event.delta() / 120

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
        elif event.key() == 68:  # d
            Primitive.DEBUG = not Primitive.DEBUG
        elif event.key() == 78:  # n
            self.nnv_window.setVisible(not self.nnv_window.isVisible())

    def set_timer_interval(self, interval):
        self.timer_interval = max(1, interval)
        self.timer.stop()
        self.timer.start(self.timer_interval, self)

    def resizeEvent(self, event):
        self.stimulation_func.set_size(self.width())
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
        self.area_size = 10

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
