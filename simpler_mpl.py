import math
import matplotlib as mpl
import matplotlib.pyplot as plt

# fig, ax = plt.subplots(constrained_layout=True, figsize=(4, 4))
# fig, axs = plt.subplot_mosaic(['A', 'B'], ...) # name and describe the layout https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot_mosaic.html
# ax.get_legend().remove() # remove a legend (another way)

# axs['Uplift'].yaxis.set_major_formatter(StrMethodFormatter('${x:0.0f}')) # apply a standard formatter e.g. floats with no decimal place and dollar sign
# ax.yaxis.set_major_formatter(lambda x, pos: f"{int(x/1000):,}k") # x will be numeric if that's what we'veplotted
# ax.yaxis.set_major_formatter(lambda x, pos: f"{x:,.1f}") # e.g. 100,000.0

# configure font
# font = {'family': 'FreeSans', 'size': 20}
# mpl.rc('font', **font)

# TODO
# figure out how to turn labels 90degree facing down
# plt.xticks(rotation=-90);

# get_xticklabels shows rendered labls but
# set_major_formatter only has the default not the rendered
# text, this seems inconsistent and is connected to
# https://github.com/matplotlib/matplotlib/issues/16140
# https://github.com/matplotlib/matplotlib/pull/16141


def set_common_mpl_styles(
    ax,
    legend=True,
    grid_axis="y",
    ylabel=None,
    xlabel=None,
    title=None,
    ymin=None,
    xmin=None,
):
    """Nice common plot configuration
    We might use it via `fig, ax = plt.subplots(constrained_layout=True, figsize=(8, 6))`
    """
    if grid_axis is not None:
        # depending on major/minor grid frequency we might
        # need the simpler form
        # ax.grid(axis=grid_axis)
        ax.grid(visible=True, which="both", axis=grid_axis)
    if legend is False:
        ax.legend_.remove()
    else:
        ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if title is not None:
        ax.set_title(title)
    if ymin is not None:
        ax.set_ylim(ymin=ymin)
    if xmin is not None:
        ax.set_xlim(xmin=xmin)


def rotate_labels(x_axis=False, y_axis=False, rotation=-90):
    if x_axis:
        plt.xticks(rotation=rotation)
    if y_axis:
        plt.yticks(rotation=rotation)


def set_commas(ax, x_axis=False, y_axis=False):
    # NOTE this may not work well e.g. on bar plots
    # in which case make a df_to_plot where index has been
    # reset, turned with string formatting into good result,
    # then index has been set again
    texts = []
    if x_axis:
        ticks = ax.get_xticks()
        tick_labels = ax.get_xticklabels()
        for label in tick_labels:
            text = label.get_text()
            texts.append(f"{int(text):,}")
        plt.xticks(ticks=ticks, labels=texts)
    if y_axis:
        ticks = ax.get_yticks()
        tick_labels = ax.get_yticklabels()
        for label in tick_labels:
            text = label.get_text()
            texts.append(f"{int(text):,}")
        plt.yticks(ticks=ticks, labels=texts)


def set_commas_olddependsonrendering(ax, on_x_axis=True, on_y_axis=True):
    '''Add commas e.g. 1_000_000 -> "1,000,000"'''
    if on_x_axis:
        axis = ax.get_xaxis()
        axis.set_major_formatter(
            mpl.ticker.FuncFormatter(lambda x, pos: format(int(x), ","))
        )
    if on_y_axis:
        axis = ax.get_yaxis()
        axis.set_major_formatter(
            mpl.ticker.FuncFormatter(lambda x, pos: format(int(x), ","))
        )


# WARNING this function is broken, I need to write a
# human_format that'll add commas as a default...
def set_human_format(ax, on_x_axis=False, on_y_axis=False, **kwargs):
    '''Add commas e.g. 1_000_000 -> "1,000,000"'''
    if on_x_axis == False and on_y_axis == False:
        raise ValueError("An axis must be chosen!")
    if on_x_axis:
        axis = ax.get_xaxis()
        axis.set_major_formatter(
            # OLD mpl.ticker.FuncFormatter(lambda x, p: f"{results_to_plot_df.index[x]:0.0f}%")
            mpl.ticker.FuncFormatter(lambda x, p: human_format(x, **kwargs))
        )
    if on_y_axis:
        axis = ax.get_yaxis()
        axis.set_major_formatter(
            # OLD mpl.ticker.FuncFormatter(lambda x, p: f"{int(x):,}")
            mpl.ticker.FuncFormatter(lambda x, p: human_format(x, **kwargs))
        )
