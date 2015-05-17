__author__ = 'arch'
from PyQt4.QtGui import QBrush, QColor
from PyQt4 import QtGui, QtCore
import sys
import math
import random

from Primitive import Primitive
from NeuralNetworkViewer import NeuralNetworkViewer


def brush(r, g, b, alpha=255):
    return QBrush(QColor(r, g, b, alpha))


class MainWindow(QtGui.QWidget):
    def __init__(self, primitive, nnv_window):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Main Windows")
        self.resize(400, 400)
        self.mouse = Mouse()
        self.prim = primitive
        self.nnv_window = nnv_window

        self.state_func, self.promotion_func, self.aver_promotion_func = [], [], []
        self.scaled_prom_func = []
        self.draw_plots = False

        # self.timer_interval = 300
        self.timer_interval = 300
        self.timer = QtCore.QBasicTimer()
        self.timer.start(self.timer_interval, self)
        self.auto_teach = False
        self.auto_teach_counter = 0

    def timerEvent(self, event):

        self.setWindowTitle("{:.4f} : {:.6f} : {:.6f} : {:.6f}".format(self.prim.state, self.prim.promotion, self.prim.average_promotion, self.prim.scaled_promotion))
        self.update_primitive_position()
        if self.draw_plots:
            self.state_func.append(self.prim.state)
            self.promotion_func.append(self.prim.promotion)
            self.aver_promotion_func.append(self.prim.average_promotion)
            self.scaled_prom_func.append(self.prim.scaled_promotion)

        state_delta = self.get_state_delta()
        # print(self.prim.promotion)

        self.prim.change_state(state_delta)
        sensors_values = [ self.get_sensor_value(x, y) for x, y in self.prim.sensors_positions()]
        self.prim.update(sensors_values)

        self.repaint()
        nnv_window.repaint()
        if self.auto_teach:
            self.mouse.but1_pressed = True
            self.auto_teach_counter -= 1
            if self.auto_teach_counter <= 0:
                self.auto_teach_counter = random.randint(500, 1000)
                self.mouse.x = random.randint(0, self.width())
                self.mouse.y = random.randint(0, self.height())
                self.mouse.area_size = random.randint(10,40)

    def get_sensor_value(self, x, y):
        if self.mouse.pressed() and math.sqrt((self.mouse.x-x)**2 + (self.mouse.y-y)**2) < self.mouse.area_size:
            if self.mouse.but1_pressed:
                return 1.0
            elif self.mouse.but2_pressed:
                return -1.0
        return 0.0

    def get_state_delta(self):
        val = 0
        if self.mouse.but1_pressed or self.mouse.but2_pressed:
            val = self.calc_intersect_value()/5000.0
            if self.mouse.but2_pressed:
                val *= -1
        # if val == 0:
        #     val = self.prim.state / -10.0
        return val

    def calc_intersect_value(self):
        dist = math.sqrt((self.mouse.x-self.prim.x)**2 + (self.mouse.y-self.prim.y)**2)
        intersect_length = max(0, self.mouse.area_size+self.prim.size-dist)
        intersect_length = min(intersect_length, self.mouse.area_size*2, self.prim.size*2)
        return (intersect_length**2) / 2

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)

        # drawing plots
        if self.draw_plots:
            zoom = 8000
            qp.setPen(QtCore.Qt.gray)
            qp.drawLine(0, Primitive.promotion_filter*zoom + 200, len(self.promotion_func), Primitive.promotion_filter*zoom + 200)
            qp.drawLine(0, -Primitive.promotion_filter*zoom + 200, len(self.promotion_func), -Primitive.promotion_filter*zoom + 200)
            qp.drawLine(0, 200, len(self.promotion_func), 200)
            qp.setPen(QtCore.Qt.darkCyan)
            for i in range(len(self.state_func)-1):
                qp.drawLine(i, -self.state_func[i]*70 + 200, i+1, -self.state_func[i+1]*70 + 200)
            qp.setPen(QtCore.Qt.blue)
            for i in range(len(self.promotion_func)-1):
                qp.drawLine(i, -self.promotion_func[i]*zoom + 200, i+1, -self.promotion_func[i+1]*zoom + 200)
            qp.setPen(QtCore.Qt.green)
            for i in range(len(self.aver_promotion_func)-1):
                qp.drawLine(i, -self.aver_promotion_func[i]*zoom + 200, i+1, -self.aver_promotion_func[i+1]*zoom + 200)
            qp.setPen(QtCore.Qt.red)
            for i in range(len(self.scaled_prom_func)-1):
                qp.drawLine(i, -self.scaled_prom_func[i]*zoom + 200, i+1, -self.scaled_prom_func[i+1]*zoom + 200)
        # drawing primitive
        qp.setPen(QtCore.Qt.black)
        qp.setBrush(brush(170, 170, 170))
        qp.drawEllipse(self.prim.x - self.prim.size,
                       self.prim.y - self.prim.size,
                       self.prim.size*2,
                       self.prim.size*2)
        # drawing sensors
        qp.setBrush(brush(0, 0, 0))
        for sensor_pos in self.prim.sensors_positions():
            qp.drawEllipse(sensor_pos[0]-3, sensor_pos[1]-3, 6, 6)
        # drawing mouse
        if self.mouse.pressed():
            self.mouse.draw(qp)

        qp.end()

    def update_primitive_position(self):
        if self.prim.x < 0:
            self.prim.x = self.width()-10
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
        print("key={} ".format(event.key()))
        if event.key() == 32:  # space
            if self.timer.isActive():
                self.timer.stop()
            else:
                self.timer.start(self.timer_interval, self)
        elif event.key() == 67:  # c
            self.state_func, self.promotion_func, self.aver_promotion_func = [], [], []
            self.scaled_prom_func = []
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
            print("context cleared")
        elif event.key() == 70:  # f
            self.mouse.fixed = not self.mouse.fixed
        elif event.key() == 65:  # a
            self.auto_teach = not self.auto_teach

    def set_timer_interval(self, interval):
        self.timer_interval = max(1, interval)
        self.timer.stop()
        self.timer.start(self.timer_interval, self)




class Mouse():
    def __init__(self):
        self.x, self.y = 0, 0
        self.fixed = False
        self.but1_pressed = False
        self.but2_pressed = False
        self.but3_pressed = False
        self.area_size = 10

    def pressed(self):
        return self.but1_pressed or self.but2_pressed or self.but3_pressed

    def draw(self, qp):
        old_brush = qp.brush()
        if self.but1_pressed:
            qp.setBrush(brush(80, 180, 60, alpha=175))
        if self.but2_pressed:
            qp.setBrush(brush(180, 60, 80, alpha=175))
        if self.but3_pressed:
            qp.setBrush(brush(60, 80, 180, alpha=175))
        qp.drawEllipse(self.x-self.area_size,
                       self.y-self.area_size,
                       self.area_size*2,
                       self.area_size*2)
        qp.setBrush(old_brush)


if __name__=='__main__':
    application = QtGui.QApplication(sys.argv)
    primitive = Primitive()
    nnv_window = NeuralNetworkViewer(primitive.brain)
    window = MainWindow(primitive, nnv_window)
    window.show()
    nnv_window.show()
    sys.exit(application.exec_())