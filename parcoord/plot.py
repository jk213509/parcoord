# -*- coding: utf-8 -*-
# python3
# Copyright (c) 2017 by Dr. Justin Klotz

import numpy as np
from typing import List
import matplotlib
from matplotlib import colors as mpl_colors, cm as mpl_cm, colorbar as mpl_colorbar, figure as mpl_figure,\
    ticker as mpl_ticker

# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

# TODO: Verify set_visible works
# TODO: Verify re-plot works
# TODO: Determine which part of code takes longest (pproject from pypi)


class ParCoord:
    def __init__(self,
                 data_sets: list):

        # Verify user input
        num_dims = len(data_sets[0])
        # dimensions
        if num_dims < 2:
            raise ValueError('Must supply data with more than one dimension.')

        # Setup figure and axes
        x = range(num_dims)
        fig = mpl_figure.Figure()
        axes = list()
        for idx in range(num_dims - 1):
            axes.append(fig.add_subplot(1, num_dims-1, idx + 1))

        # Store, initialize values
        self.fig = fig
        self._axes = axes
        self._ax_color_bar = None
        self._x = x
        self._data_sets = None
        self._data_sets_info = None
        self._num_dims = num_dims
        self._colors = None
        self._scores = None
        self._scores_norm_min = None
        self._scores_norm_max = None
        self._color_style = None
        self._color_map_norm = None
        self._use_variable_line_width = False
        self._sorted_scores_indices = None

        self._set_data(data_sets)

    def _set_data(self,
                  data_sets: list):
        # make sure there are no nan's
        for data_set in data_sets:
            if np.nan in data_set:
                raise ValueError('Argument "data_sets" must not contain nan\'s')

        self._data_sets = data_sets

    def reset_data(self,
                   data_sets: list):
        self._scores = None
        self._sorted_scores_indices = None
        self._colors = None
        self._set_data(data_sets)

    def set_visible(self,
                    visible: List[bool]):
        if len(visible) != len(self._data_sets):
            raise ValueError('List "visible" passed to set_visible must be same length as number of data sets')
        if self._scores is not None:
            visible = [visible[idx] for idx in self._sorted_scores_indices]
        for ax in self._axes:
            for idx, line in enumerate(ax.lines):
                if not isinstance(visible[idx], bool):
                    raise ValueError('List "visible" passed to set_visible must only contain booleans.')
                line.set_visible(visible[idx])

    def save_fig(self,
                 path: str):
        try:
            self.fig.savefig(path)
        except:
            raise ValueError('Could not save file to path ' + path)

    def plot(self,
             num_ticks: int=7,
             line_width=1.1,
             y_min: list or None=None,
             y_max: list or None=None):

        # Calculate data set limits
        data_sets_info = list()
        for idx, m in enumerate(zip(*self._data_sets)):
            if y_min is not None:
                mn = y_min[idx]
            else:
                mn = min(m)
            if y_max is not None:
                mx = y_max[idx]
            else:
                mx = max(m)
            if mn == mx:
                mn -= 0.5
                mx = mn + 1.
            r = float(mx - mn)
            data_sets_info.append({'min': mn, 'max': mx, 'range': r})

        # Normalize the data sets
        norm_data_sets = list()
        for ds in self._data_sets:
            nds = [(value - data_sets_info[dimension]['min']) / data_sets_info[dimension]['range']
                   for dimension, value in enumerate(ds)]
            norm_data_sets.append(nds)

        # Clear axes in case they were plotted on previously
        for ax in self._axes:
            ax.clear()

        # Plot the data sets on all the subplots
        for i, ax in enumerate(self._axes[:self._num_dims]):
            for dsi in range(len(norm_data_sets)):
                if self._colors is not None:
                    if self._scores is not None and self._use_variable_line_width and self._scores[0]!=self._scores[-1]:
                        min_width = line_width
                        max_width = min_width + 3
                        line_width_iter = min_width + (max_width - min_width)*(self._scores[-1] - self._scores[dsi])\
                                          / (self._scores[-1] - self._scores[0])
                    else:
                        line_width_iter = line_width
                    ax.plot(self._x, norm_data_sets[dsi], linewidth=line_width_iter, color=self._colors[dsi])
                else:
                    ax.plot(self._x, norm_data_sets[dsi], linewidth=line_width)
            ax.set_xlim([self._x[i], self._x[i+1]])

        # Set the axis ticks
        for dimension, (ax, xx) in enumerate(zip(self._axes[:self._num_dims], self._x[:self._num_dims])):
            # x-axis
            ax.xaxis.set_major_locator(mpl_ticker.FixedLocator([xx]))
            # y-axis
            ax.yaxis.set_major_locator(mpl_ticker.FixedLocator(list(np.linspace(0, 1, num_ticks))))
            min_ = data_sets_info[dimension]['min']
            max_ = data_sets_info[dimension]['max']
            labels = ['{:4.2f}'.format(val) for val in np.linspace(min_, max_, num_ticks)]
            ax.set_yticklabels(labels, color='k', weight='semibold')  # backgroundcolor='0.75'

        # Move the final axis' ticks to the right-hand side
        if len(self._axes) < self._num_dims:
            ax_last = self._axes[-1].twinx()  # create last axis if this is not a re-plot
        else:
            ax_last = self._axes[-1]
        dimension_last = self._num_dims-1
        # x-axis
        ax_last.xaxis.set_major_locator(mpl_ticker.FixedLocator([self._x[-2], self._x[-1]]))
        # y-axis
        ax_last.yaxis.set_major_locator(mpl_ticker.FixedLocator(list(np.linspace(0, 1, num_ticks))))
        num_ticks = len(ax_last.get_yticklabels())
        min_ = data_sets_info[dimension_last]['min']
        max_ = data_sets_info[dimension_last]['max']
        labels = ['{:4.2f}'.format(val) for val in np.linspace(min_, max_, num_ticks)]
        ax_last.set_yticklabels(labels, color='k', weight='semibold')

        # Stack the subplots
        self.fig.subplots_adjust(wspace=0)

        # Adjust plot borders, labels
        self._axes.append(ax_last)
        for ax in self._axes:
            ax.tick_params(direction='inout', length=10, width=1)
            ax.tick_params(axis='x', pad=20, labelsize=12)
            ax.set_ylim(0, 1)
            ax.spines['bottom'].set_visible(False)
            ax.spines['top'].set_visible(False)

    def set_colors(self,
                   colors: str or list):
        if isinstance(colors, str):
            colors = [colors] * len(self._data_sets)
        self._colors = colors
        self._scores = None

    def set_scores(self,
                   scores: list,
                   color_map_norm_type=mpl_colors.Normalize,
                   color_style: str='cool',
                   scores_norm_min: int or float=None,
                   scores_norm_max: int or float=None,
                   plot_high_scores_on_top: bool=True,
                   use_variable_line_width: bool=False):
        # Create color map
        if scores_norm_min is None:
            scores_norm_min = min(scores)
        if scores_norm_max is None:
            scores_norm_max = max(scores)
        color_map_norm = color_map_norm_type(vmin=scores_norm_min, vmax=scores_norm_max, clip=True)
        color_map = mpl_cm.ScalarMappable(cmap=color_style, norm=color_map_norm)
        # Sort data sets, scores
        sorted_scores_indices = list(np.argsort(scores))
        if not plot_high_scores_on_top:
            sorted_scores_indices = sorted_scores_indices[::-1]
        self._data_sets = [self._data_sets[idx] for idx in sorted_scores_indices]
        scores = [scores[idx] for idx in sorted_scores_indices]
        # Set plot colors
        colors = list()
        for score in scores:
            colors.append(color_map.to_rgba(score))
        # Store values
        self._color_style = color_style
        self._colors = colors
        self._scores = scores
        self._scores_norm_min = scores_norm_min
        self._scores_norm_max = scores_norm_max
        self._color_map_norm = color_map_norm
        self._use_variable_line_width = use_variable_line_width
        self._sorted_scores_indices = sorted_scores_indices

    def set_labels(self,
                   labels: list):
        for idx in range(self._num_dims - 1):
            self._axes[idx].set_xticklabels([labels[idx]], color='k')
        self._axes[self._num_dims - 1].set_xticklabels([labels[self._num_dims-2], labels[self._num_dims-1]], color='k')

    def add_color_bar(self,
                      label: str or None=None):
        if self._scores is not None:
            if self._ax_color_bar is None:  # if axis for color bar not yet created
                # create axis for color bar
                self._ax_color_bar = mpl_colorbar.make_axes(self._axes, Location='right')[0]
            self._ax_color_bar.set_ylim([self._scores_norm_min, self._scores_norm_max])
            cb = mpl_colorbar.ColorbarBase(self._ax_color_bar,
                                           cmap=self._color_style,
                                           norm=self._color_map_norm,
                                           orientation='vertical',
                                           )
            if label:
                cb.set_label(label)
        else:
            raise ValueError('Set scores before adding a color bar.')
