from math import *
import numpy as np
import matplotlib.pyplot as plt


def plot(func):
    exec_code = """def f(x):
        return """ + func
    exec(exec_code)
    x = np.arange(-100, 100, 0.1)
    y = []
    for i in x:
        y.append(f(i))
    plot = plt.plot(x, y)
    return plot
