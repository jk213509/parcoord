# -*- coding: utf-8 -*-
# python3
# Copyright (c) 2017 by Dr. Justin Klotz

import sys
import random
from parcoord.plot import parallel_coordinates
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
scores = [random.uniform(0, 1) for _ in range(60)]

# Make x-axis tick labels
var_labels = ['var' + str(idx) for idx in range(num_vars)]

# Examples
mode = 4
fig_pc = None
if mode == 0:  # basic
    fig_pc = parallel_coordinates(data)
elif mode == 1:  # single color is specified
    fig_pc = parallel_coordinates(data, x_labels=var_labels, num_ticks=6, colors='r')
elif mode == 2:  # color list is specified
    fig_pc = parallel_coordinates(data, x_labels=var_labels, num_ticks=6, colors=colors, line_width=.9)
elif mode == 3:  # color map is specified
    fig_pc = parallel_coordinates(data, x_labels=var_labels, num_ticks=6, scores=scores, color_map_type='cool')
elif mode == 4:  # color map is specified with additional inputs
    color_map_norm_type = matplotlib.colors.LogNorm
    fig_pc = parallel_coordinates(data, x_labels=var_labels, num_ticks=6, scores=scores, color_map_type='magma',
                                  color_map_norm_type=color_map_norm_type, scores_norm_min=1e-5,
                                  scores_norm_max=max(scores), plot_high_scores_on_top=False, line_width=1.5)

# Show in PyQt
# App
qApp = QtWidgets.QApplication(sys.argv)
# Window
window = QtWidgets.QMainWindow()
window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
# Widget
widget = QtWidgets.QWidget(window)
# Canvas
canvas = FigureCanvas(fig_pc)
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
