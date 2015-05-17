__author__ = 'arch'
import math
import random
from NeuralNetwork.NeuralNetwork import NeuralNetwork


def generate_answer(inp):
    sensor_count = len(inp)
    angle = math.pi * 2.0 / sensor_count
    x = sum(( math.cos(angle*i) for i in range(sensor_count) if inp[i]==1.0 ))
    x = min(1.0, max(-1.0, x))
    y = sum(( math.sin(angle*i) for i in range(sensor_count) if inp[i]==1.0 ))
    y = min(1.0, max(-1.0, y))
    return x, y


def generate_test(sensor_count, involved_sensor_count, offset):
    inp = [0.0] * sensor_count
    for i in range(offset, offset+involved_sensor_count):
        inp[i % sensor_count] = 1.0
    return inp, generate_answer(inp)


def create_tests(sensor_count):
    test_db = []
    for involved_sensor_count in range(1, sensor_count):
        for offset in range(sensor_count):
            test_db.append(generate_test(sensor_count, involved_sensor_count, offset))
    return test_db


def make_net(sensor_count= 16):
    net = NeuralNetwork([sensor_count, 7, 2], learn_rate=0.05)
    test_db = create_tests(sensor_count)
    # print "\n".join([str(x) for x in test_db])
    random.shuffle(test_db)

    for i in range(5):
        answ = net.calculate(test_db[i][0])
        print(test_db[i][0], test_db[i][1], answ)

    errs = []
    for _ in range(200):
        epoch_error = 0
        for test in test_db:
            y = net.calculate(test[0])
            err = math.sqrt((test[1][0]-y[0])**2 + (test[1][1]-y[1])**2)
            if err < 1.0:
                net.teach(-0.004)
            else:
                net.teach(0.004)
            epoch_error += err
        epoch_error /= len(test_db)
        errs.append(epoch_error)
        print epoch_error

    for i in range(10):
        answ = net.calculate(test_db[i][0])
        print(test_db[i][0], test_db[i][1], answ)

    if __name__=='__main__':
        plt.plot(errs)
        plt.show()

    return net


if __name__=='__main__':
    import matplotlib.pyplot as plt
    make_net()