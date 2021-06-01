from math import *
import numpy as np
import matplotlib.pyplot as plt

f = None


def plot(func, left, right):
    #     f = None
    #     exec_code = """f = 2
    # print(f)"""
    #     exec(exec_code, locals())
    #     return None
    exec_code = """
def g(x):
    return """ + func + "\n"
    # exec_code += "f = g"
    exec(exec_code, globals())
    if left > right:
        left, right = right, left

    range = np.arange(left, right, (right - left) / 1e6)
    x = []
    y = []
    print(len(range))
    for i in range:
        y.append(g(i))
        x.append(i)

    return x, y


def show(line1, line2):
    fig = plt.figure()
    ax1 = plt.subplot(211)
    ax1.plot(line1[0], line1[1], label='original')
    ax1.axis
    ax2 = plt.subplot(212)
    ax2.plot(line2[0], line2[1], label='diff')
    ax1.grid()
    ax2.grid()
    ax1.set_title("function", color='w')
    ax2.set_title("diff", color='w')
    # ax1.label_outer()
    # ax2.label_outer()
    ax1.tick_params(colors='w', which='both')
    ax2.tick_params(colors='w', which='both')
    # plt.axes(ymargin=-0.1)
    ax1.autoscale(enable=True, axis='y', tight=True)
    ax2.autoscale(enable=True, axis='y', tight=True)
    print(ax1.get_ylim())
    ymin, ymax = ax1.get_ylim()
    if abs(ymin) > 1000 or abs(ymax) > 1000:
        if abs(ymin) > 1000:
            ymin = -100
        if abs(ymax) > 1000:
            ymax = 100
        ymin, ymax = ax1.set_ylim(ymin, ymax)
    ymin, ymax = ax2.get_ylim()
    if abs(ymin) > 1000 or abs(ymax) > 1000:
        if abs(ymin) > 1000:
            ymin = -100
        if abs(ymax) > 1000:
            ymax = 100
        ymin, ymax = ax2.set_ylim(ymin, ymax)
    plt.show()
