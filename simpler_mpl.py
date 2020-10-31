import math
import matplotlib as mpl


# fig, ax = plt.subplots(constrained_layout=True)

# configure font
#font = {'family': 'FreeSans', 'size': 20}
#mpl.rc('font', **font)

# TODO
# figure out how to turn labels 90degree facing down

def set_commas(ax, on_x_axis=True, on_y_axis=True):
    '''Add commas e.g. 1_000_000 -> "1,000,000"'''
    if on_x_axis:
        axis = ax.get_xaxis()
        axis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    if on_y_axis:
        axis = ax.get_yaxis()
        axis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))


def set_common_mpl_styles(ax, legend=True, grid_axis='y', ylabel=None, xlabel=None, title=None):
    ax.grid(axis=grid_axis)
    if legend:
        ax.legend(frameon=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if title is not None:
        ax.set_title(title)


def set_human_format(ax, on_x_axis=False, on_y_axis=False, **kwargs):
    '''Add commas e.g. 1_000_000 -> "1,000,000"'''
    if on_x_axis == False and on_y_axis == False:
        raise ValueError('An axis must be chosen!')
    if on_x_axis:
        axis = ax.get_xaxis()
        axis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: human_format(x, **kwargs)))
    if on_y_axis:
        axis = ax.get_yaxis()
        axis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: human_format(x, **kwargs)))


def human_format(num, precision=2, suffixes=['', 'k', 'M', 'G'], prefix='', trim_0_decimals=False):
    '''Turn 1_234_000 into 1.23M'''
    # TODO consider different suffixes, either a fixed set
    # or even a lookup with a dict and a nice label
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
        short_form = num / 1000.0 ** m
        short_form_template = f'{short_form:.{precision}f}'
        if precision > 0 and trim_0_decimals:
            if short_form == int(short_form):
                # no decimals
                short_form = int(short_form)
                short_form_template = f'{short_form}'
        output = sgn + prefix + short_form_template + f'{suffixes[abs(m)]}'
        #output = sgn + prefix + f'{num/1000.0**m:.{precision}f}{suffixes[abs(m)]}'
    else:
        # nasty hack to avoid pennies turning into kilo
        output = sgn + prefix + f'{num:.{2}f}'
    return output


def test_human_format():
    assert human_format(1000, precision=0) == "1k"
    assert human_format(1000, prefix="£") == "£1.00k" # NOTE this looks stupid!
    assert human_format(1000, prefix="£", trim_0_decimals=True) == "£1k" 
    assert human_format(2_500_000, prefix="£", precision=1) == "£2.5M" 
    assert human_format(-2_500_000, prefix="£", precision=1) == "-£2.5M" 
    assert human_format(-2_000_000, prefix="£", precision=1) == "-£2.0M" 
    assert human_format(-2_000_000, prefix="£", precision=1, trim_0_decimals=True) == "-£2M" 
    assert human_format(2_000, prefix="£", precision=2)  == "£2.00k" 


if __name__ == "__main__":
    print(human_format(-2_500_000, prefix="£", precision=1))
    print(human_format(-2_000_000, prefix="£", precision=1))
