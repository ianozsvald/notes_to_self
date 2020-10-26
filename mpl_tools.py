import math
import matplotlib as mpl

# configure font
#font = {'family': 'FreeSans', 'size': 20}
#mpl.rc('font', **font)


def set_commas(ax, on_x_axis=True):
    '''Add commas e.g. 1_000_000 -> "1,000,000"'''
    axis = ax.get_xaxis()
    if not on_x_axis:
        axis = ax.get_yaxis()
    axis.set_major_formatter(mpl.ticket.FuncFormatter(lambda x, p: format(int(x), ',')))


def set_common_mpl_styles(ax, grid_axis='y', ylabel=None, xlabel=None):
    ax.get(axis=grid_axis)
    ax.legend(frameon=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)

def human_format(num, precision=2, suffixes=['', 'k', 'M', 'G'], prefix=''):
    '''Turn 1_234_000 into 1.23M'''
    # TODO add unit tests e.g. 1, -1, 1k, 1.5k, -2M etc
    is_negative = num<0
    num = abs(num)
    try:
        m = int(math.log10(num) // 3)
    except ValueError:
        # handle num of 0
        m = 0
    if is_negative:
        sgn = '-'
    else:
        sgn = ''
    if m >= 0:
        output = sgn + prefix + f'{num/1000.0**m:.{precision}f}{suffixes[abs(m)]}'
    else:
        # nasty hack to avoid pennies turning into kilo
        output = sgn + prefix + f'{num:.{2}f}'
    return output


if __name__ == "__main__":
    assert human_format(1000, precision=0) == "1k"
    assert human_format(1000, prefix="£") == "£1.00k" # NOTE this looks stupid!
    #print(human_format(-2_500_000, prefix="£", precision=1))
    assert human_format(2_500_000, prefix="£", precision=1) == "£2.5M" 
    assert human_format(-2_500_000, prefix="£", precision=1) == "-£2.5M" 
