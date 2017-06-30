# -*- coding: utf-8 -*-
# python3
# Copyright (c) 2017 by Dr. Justin Klotz

import numpy as np
import matplotlib
from matplotlib import colors as mpl_colors, cm as mpl_cm, colorbar as mpl_colorbar, figure as mpl_figure,\
    ticker as mpl_ticker

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')


def parallel_coordinates(data_sets, x_labels: list=None, num_ticks: int=7, colors=None, scores: list=None,
                         color_map_type='magma', color_map_norm_type=mpl_colors.Normalize,
                         scores_norm_min=None, scores_norm_max=None, plot_high_scores_on_top: bool=True,
                         line_width=1.1):
    """
    This function plots the values of data set coordinates on parallel axes with connecting lines
    Note: append color map string with _r to reverse the colors
    :param data_sets: coordinate values
    :param x_labels: (optional) string values of coordinate names
    :param num_ticks: (optional) number of ticks on y-axes
    :param colors: (optional) single color, or list of colors for each data set
    :param scores: (optional) used to assign color to each data set
    :param color_map_type: (optional) string of color map type (e.g., 'magma')
    :param color_map_norm_type: (optional) matplotlib.colors instance (e.g., matplotlib.colors.Normalize)
    :param scores_norm_min: (optional) lower normalization constant for color representation of data sets
    :param scores_norm_max: (optional) upper normalization constant for color representation of data sets
    :param plot_high_scores_on_top: (optional) plot high score data sets on top if True, bottom if False
    :param line_width: (optional) data set plot line width
    :return: instance of matplotlib.figure.Figure
    """

    # Verify user input
    dims = len(data_sets[0])
    # dimensions
    if dims < 2:
        raise ValueError('Must supply data with more than one dimension.')
    if x_labels is not None and len(x_labels) != dims:
        raise ValueError('If x_labels is specified, its length must be equal to the number of coordinates')
    # make sure there are no nan's
    for data_set in data_sets:
        if np.nan in data_set:
            raise ValueError('Argument "data_sets" must not contain nan\'s')
    if scores is not None and np.nan in scores:
        raise ValueError('Argument "scores" must not contain nan\'s')
    if scores_norm_min is not None and not isinstance(scores_norm_min, (int, float)):
        raise ValueError('Argument "scores_norm_min" must be a number')
    if scores_norm_max is not None and not isinstance(scores_norm_max, (int, float)):
        raise ValueError('Argument "scores_norm_max" must be a number')
    # colors
    if colors is not None and isinstance(colors, str):
        colors = [colors] * len(data_sets)
    # scores and associated optional inputs
    use_color_bar = False
    if colors is None and scores is not None:
        use_color_bar = True
    else:
        scores = list()  # to avoid IDE warnings...
    if use_color_bar and len(data_sets) != len(scores):
        raise ValueError('Number of data sets must be equal to the number of scores')
    if use_color_bar and scores_norm_min is None:
        scores_norm_min = min(scores)
    if use_color_bar and scores_norm_max is None:
        scores_norm_max = max(scores)
    if not isinstance(color_map_type, str):
        raise ValueError('Variable color_map_type must be a string')

    # Setup figure and axes
    x = range(dims)
    fig = mpl_figure.Figure()
    axes = list()
    num_axes = dims-1
    if use_color_bar:
        num_axes += 1
    for idx in range(dims-1):
        axes.append(fig.add_subplot(1, num_axes, idx+1))

    # Calculate the limits on the data
    data_sets_info = list()
    for m in zip(*data_sets):
        mn = min(m)
        mx = max(m)
        if mn == mx:
            mn -= 0.5
            mx = mn + 1.
        r = float(mx - mn)
        data_sets_info.append({'min': mn, 'max': mx, 'range': r})

    # Normalize the data sets
    norm_data_sets = list()
    for ds in data_sets:
        nds = [(value - data_sets_info[dimension]['min']) / data_sets_info[dimension]['range']
               for dimension, value in enumerate(ds)]
        norm_data_sets.append(nds)
    data_sets = norm_data_sets

    # Plot the data sets on all the subplots
    color_map_norm_scores = None
    color_map_scores = None
    sorted_scores_indices = None
    if use_color_bar:
        color_map_norm_scores = color_map_norm_type(vmin=scores_norm_min, vmax=scores_norm_max, clip=True)
        color_map_scores = mpl_cm.ScalarMappable(cmap=color_map_type, norm=color_map_norm_scores)
        sorted_scores_indices = list(np.argsort(scores))
        if not plot_high_scores_on_top:
            sorted_scores_indices = sorted_scores_indices[::-1]
    for i, ax in enumerate(axes):
        for dsi in range(len(data_sets)):
            if colors is not None:
                ax.plot(x, data_sets[dsi], colors[dsi], linewidth=line_width)
            elif use_color_bar:
                # optional plot argument zorder didn't seem to work...
                ax.plot(x, data_sets[sorted_scores_indices[dsi]], linewidth=line_width,
                        color=color_map_scores.to_rgba(scores[sorted_scores_indices[dsi]]))
            else:
                ax.plot(x, data_sets[dsi], linewidth=line_width)
        ax.set_xlim([x[i], x[i+1]])

    # Set the axis ticks
    for dimension, (axx, xx) in enumerate(zip(axes, x[:-1])):
        # x-axis
        axx.xaxis.set_major_locator(mpl_ticker.FixedLocator([xx]))
        if x_labels is not None:
            axx.set_xticklabels([x_labels[dimension]], color='k')
        # y-axis
        axx.yaxis.set_major_locator(mpl_ticker.FixedLocator(list(np.linspace(0, 1, num_ticks))))
        min_ = data_sets_info[dimension]['min']
        range_ = data_sets_info[dimension]['range']
        labels = ['{:4.2f}'.format(min_ + range_*idx/num_ticks) for idx in range(num_ticks+1)]
        axx.set_yticklabels(labels, color='k', weight='semibold')  # backgroundcolor='0.75'

    # Move the final axis' ticks to the right-hand side
    axx_last = axes[-1].twinx()
    dimension = dims-1
    # x-axis
    axx_last.xaxis.set_major_locator(mpl_ticker.FixedLocator([x[-2], x[-1]]))
    if x_labels is not None:
        axx_last.set_xticklabels([x_labels[-2], x_labels[-1]], color='k')
    # y-axis
    axx_last.yaxis.set_major_locator(mpl_ticker.FixedLocator(list(np.linspace(0, 1, num_ticks))))
    num_ticks = len(axx_last.get_yticklabels())
    min_ = data_sets_info[dimension]['min']
    range_ = data_sets_info[dimension]['range']
    labels = ['{:4.2f}'.format(min_ + range_ * idx / num_ticks) for idx in range(num_ticks + 1)]
    axx_last.set_yticklabels(labels, color='k', weight='semibold')

    # Stack the subplots
    fig.subplots_adjust(wspace=0)

    # Adjust plot borders, labels
    axes.append(axx_last)
    for axx in axes:
        axx.tick_params(direction='inout', length=10, width=1)
        axx.tick_params(axis='x', pad=20, labelsize=12)
        axx.set_ylim(0, 1)
        axx.spines['bottom'].set_visible(False)
        axx.spines['top'].set_visible(False)

    # Add color bar
    if use_color_bar:
        pos_last_axx = axes[-1].get_position().bounds
        axx_color_bar = fig.add_axes([pos_last_axx[0] + pos_last_axx[2] + .05, pos_last_axx[1], .05, pos_last_axx[3]])
        cb1 = mpl_colorbar.ColorbarBase(axx_color_bar, cmap=color_map_type, norm=color_map_norm_scores,
                                        orientation='vertical')
        cb1.set_label('Some Units')
        fig.subplots_adjust(wspace=0)

    return fig
