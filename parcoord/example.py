# -*- coding: utf-8 -*-
# python3
# Copyright (c) 2017 by Dr. Justin Klotz

import sys
import time
import random
from parcoord.plot import ParCoord
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.colors
import matplotlib

# Make colors and coordinate values for example
# red
num_vars = 7
base = [0,   0,  5,   5,  0, 5, 25]
scale = [1.5, 2., 1.0, 2., 2., .5, .3]
data = [[base[x] + random.uniform(0., 1.)*scale[x] for x in range(num_vars)] for _ in range(30)]
colors = ['r'] * 30
# blue
base = [3,   6,  0,   1,  3, 2, 30]
scale = [1.5, 2., 2.5, 2., 2., 1.0, .4]
data.extend([[base[x] + random.uniform(0., 1.)*scale[x] for x in range(num_vars)] for _ in range(30)])
colors.extend(['b'] * 30)

# Scores for example
scores = [5*random.uniform(0, 1) for _ in range(60)]

# Make x-axis tick labels
var_labels = ['var' + str(idx) for idx in range(num_vars)]
# Examples
mode = 4
par_co = None
t_start = time.time()
if mode == 0:  # basic
    par_co = ParCoord(data)
    par_co.plot()
elif mode == 1:  # single color is specified
    par_co = ParCoord(data)
    par_co.set_colors('r')
    par_co.plot(num_ticks=6)
    par_co.set_labels(var_labels)
elif mode == 2:  # color list is specified
    par_co = ParCoord(data)
    par_co.set_colors(colors)
    par_co.plot(num_ticks=6,
                line_width=.9)
    par_co.set_labels(var_labels)
elif mode == 3:  # color map is specified
    par_co = ParCoord(data)
    par_co.set_scores(scores)
    par_co.plot(num_ticks=6)
    par_co.set_labels(var_labels)
    par_co.add_color_bar()
elif mode == 4:  # color map is specified with additional inputs
    y_min = [min(col)-.1*(max(col)-min(col)) for col in zip(*data)]
    y_max = [max(col)+.1*(max(col)-min(col)) for col in zip(*data)]
    par_co = ParCoord(data)
    par_co.set_scores(scores=scores,
                      color_style='magma',
                      color_map_norm_type=matplotlib.colors.LogNorm,
                      scores_norm_min=min(scores),
                      scores_norm_max=max(scores),
                      plot_high_scores_on_top=False,
                      use_variable_line_width=True)
    par_co.plot(num_ticks=6,
                line_width=1.5,
                y_min=y_min,
                y_max=y_max)
    par_co.set_labels(var_labels)
    par_co.add_color_bar(label='Test Label')
fig = par_co.fig
print('Plotting took ' + str(time.time()-t_start) + ' seconds.')

# Show in PyQt
# App
qApp = QtWidgets.QApplication(sys.argv)
# Window
window = QtWidgets.QMainWindow()
window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
# Widget
widget = QtWidgets.QWidget(window)
# Canvas
canvas = FigureCanvas(fig)
canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
canvas.updateGeometry()
# Add canvas to widget
l = QtWidgets.QVBoxLayout(widget)
l.addWidget(canvas)
widget.setFocus()
window.show()
window.setCentralWidget(widget)
# Execute
sys.exit(qApp.exec_())
