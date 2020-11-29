from functools import partial
import pandas as pd
import numpy as np
from IPython.display import display
import pytest
from labelling import format_to_base_10


# GroupBy notes
# dfs.groupby([dfs.date.dt.year]) # can group on Series rather than name

# for Pandas mapping of .dt.dayofweek to a nice name
dayofweek_dict = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def show_all(x, head=999, tail=999):
    """List more rows of DataFrame and Series results than usual"""
    from IPython.display import display

    head = min(x.shape[0], head)
    tail = min(x.shape[0]-head, 0)

    if head > 0:
        with pd.option_context("display.max_rows", head):
            display(x)
    if tail > 0:
        if head > 0:
            print('...')
        with pd.option_context("display.max_rows", tail):
            display(x.tail(tail))

# TODO consider adding flatten index
# https://github.com/dexplo/minimally_sufficient_pandas/blob/master/minimally_sufficient_pandas/_pandas_accessor.py#L42
        
# attrib: https://github.com/dexplo/minimally_sufficient_pandas/blob/master/minimally_sufficient_pandas/_pandas_accessor.py#L130        
# TODO copied in by ian, it might not work! remove self, try it...
def display2TOTRY(df, top=100, bottom=0, max_columns=None):
        """
        Display the top/bottom n rows of the DataFrame. This only displays the 
        DataFrame visually in the output and does NOT return it. None is 
        always returned. Use the head/tail methods to return a DataFrame
        Parameters
        ----------
        top : int, default 100
            Number of rows to display from the top of the DataFrame.
            When <=0, no DataFrame is displayed
        bottom : int, default 0
            Number of rows to display from the bottom of the DataFrame.
            When <=0, no DataFrame is displayed
        max_columns : int, default None
            Controls the pd.options.display.max_columns property. 
            When None (default), all column get displayed.
        Returns
        -------
        None
        """
        with pd.option_context('display.max_rows', None, 'display.max_columns', max_columns):
            if top > 0:
                display(df.head(top).style.set_caption(f'Top {top} rows'))
            if bottom > 0:
                display(df.tail(bottom).style.set_caption(f'Bottom {bottom} rows'))    


# TODO
# check value_counts in a Notebook with use_display=True
def value_counts_pct(ser, rows=10, use_display=False):
    """Prettier value counts, returns dataframe of counts & percents"""
    vc1 = ser.value_counts(dropna=False)
    vc2 = ser.value_counts(dropna=False, normalize=True)
    df = pd.DataFrame({"count": vc1, "pct": vc2 * 100})
    df["pct_cum"] = df.pct.cumsum()
    if use_display:
        # use style as that's CSS/HTML only for a Notebook
        display(df[:rows].style.format({"pct": "{:0.1f}%"}))
    else:
        formatters = {"pct": "{:0.1f}%".format, "pct_cum": "{:0.1f}%".format}
        print(df.to_string(formatters=formatters))
    rows_not_shown = max(df.shape[0] - rows, 0)
    print(f"Total rows not shown {rows_not_shown} of {df.shape[0]}")
    return df


# TODO add test
def flatten_multiindex(gpby, index=False, columns=False):
    """Flatten MultiIndex to flat index after e.g. groupby"""
    assert index==True or columns==True
    if index is True:
        new_flat_index = [
            "_".join(str(s) for s in multi_index) for multi_index in gpby.index.values
        ]
        # gpby = gpby.reset_index(drop=True)
        gpby.index = new_flat_index
    if columns is True:
        new_flat_index = [
            "_".join(str(s) for s in multi_index) for multi_index in gpby.columns.values
        ]
        # gpby = gpby.reset_index(drop=True)
        gpby.columns = new_flat_index
    return gpby


# TODO add test
# TODO let me label <= >= for the extremes, maybe let me make a nice range with a convenience fist?
# int_index._data.to_numpy()[0] this gives Interval items, maybe I need to override this somehow to build a better display?
# pandas._libs.interval.Interval from type(int_index._data.to_numpy()[0])
def bin_series(dist, bin_edges):
    int_index = pd.IntervalIndex.from_breaks(bin_edges, closed="left")
    cat = pd.cut(dist, int_index)
    return int_index, cat


def test_bin_series():
    dist = np.array([-100, 0, 5])
    bin_edges = [-np.inf, -1000, 0, 1000]
    int_index, counted = bin_series(dist, bin_edges)
    assert (counted.value_counts().values == np.array([0, 1, 2])).all()
    display(counted.value_counts().sort_index(ascending=True))


# TODO make right-closed too
def label_interval(interval, format_fn=None, **kwargs):
    left = interval.left
    if not np.isinf(left):
        if format_fn is not None:
            left = format_fn(left, **kwargs)
    right = interval.right
    if not np.isinf(right):
        if format_fn is not None:
            right = format_fn(right, **kwargs)
    if interval.closed_left:
        if np.isinf(interval.left):
            label = f"< {right}"
        elif np.isinf(interval.right):
            label = f">= {left}"
        else:
            label = f"[{left} - {right})"

    return label


def test_label_interval():
    bin_edges = [-np.inf, -1000, 0, np.inf]
    int_index = pd.IntervalIndex.from_breaks(bin_edges, closed="left")
    interval = int_index._data.to_numpy()[0]  # Interval(-inf, -1000.0, closed='left')
    assert label_interval(interval) == "< -1000.0"
    interval = int_index._data.to_numpy()[1]  # Interval(-1000.0, 0.0, closed='left')
    assert label_interval(interval) == "[-1000.0 - 0.0)"
    interval = int_index._data.to_numpy()[2]  # Interval(0.0, 1000.0, closed='left')
    assert label_interval(interval) == ">= 0.0"

    interval = int_index._data.to_numpy()[0]
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True) == "< -1k"
    interval = int_index._data.to_numpy()[1]
    assert (
        label_interval(interval, format_to_base_10, trim_0_decimals=True) == "[-1k - 0)"
    )
    interval = int_index._data.to_numpy()[2]
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True) == ">= 0"

    interval = int_index._data.to_numpy()[0]
    assert (
        label_interval(interval, format_to_base_10, trim_0_decimals=True, prefix="£")
        == "< -£1k"
    )
    interval = int_index._data.to_numpy()[1]
    assert (
        label_interval(interval, format_to_base_10, trim_0_decimals=True, prefix="£")
        == "[-£1k - £0)"
    )


def make_bin_edges(desc):
    """desc=='0 1 ... 5' -> -np.inf, 0, 1, 2, 3, 4, 5, np.inf"""
    parts = desc.split(' ')
    if False:
        try:
            # 
            start = int(parts[0])
            step = int(parts[1]) - int(parts[0])
            end = int(parts[3])
            bins = np.arange(start, end, step)
            bins = np.concatenate(([-np.inf], bins, [end], [np.inf]))
        except ValueError:
            pass
    # hopefully we have floats, if not this will just die
    start = float(parts[0])
    step = float(parts[1]) - float(parts[0])
    end = float(parts[3])
    num = round((end - start) / step) + 1
    print(start, end, step, num)
    bins = np.linspace(start, end, num=num)
    bins = np.concatenate(([-np.inf], bins, [np.inf]))
    return bins


def test_make_bin_edges():
    bins = make_bin_edges("1 2 ... 5")
    assert (bins == np.array([-np.inf, 1, 2, 3, 4, 5, np.inf])).all()
    bins = make_bin_edges("-5 -3 ... 5")
    assert (bins == np.array([-np.inf, -5, -3, -1, 1, 3, 5, np.inf])).all()
    bins = make_bin_edges("-0.5 -0.4 ... -0.3")
    np.testing.assert_allclose(bins, np.array([-np.inf, -0.5, -0.4, -0.3, np.inf]))
    bins = make_bin_edges("-0.5 -0.4 ... 0.1")
    np.testing.assert_allclose(bins, np.array([-np.inf, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, np.inf]), atol=1e-5)
    bins = make_bin_edges("0.0 0.1 ... 0.5")
    np.testing.assert_allclose(bins, np.array([-np.inf, 0, 0.1, 0.2, 0.3, 0.4, 0.5, np.inf]), atol=1e-5)


# TODO should we return the result or modify in place?
def apply_labelling(df_ser, format_fn=None, **kwargs):
    """Modify index using labelling function"""
    label_interval_args = partial(label_interval, format_fn=format_fn, **kwargs)
    new_index = df_ser.index.map(label_interval_args)
    df_ser.index = new_index


def test_apply_labelling():
    items = [1, 1, 1, 2, 3, ]
    df = pd.DataFrame({'items': items})
    bin_edges = make_bin_edges("0 1 ... 2")
    int_index, counted = bin_series(items, bin_edges)
    vc = counted.value_counts()
    apply_labelling(vc, format_to_base_10, prefix='', precision=0)
    assert vc.index[0] == '< 0'
    assert (vc.index == ['< 0', '[0 - 1)', '[1 - 2)', '>= 2']).all()
    assert (vc.values == [0, 0, 3, 2]).all()

if __name__ == "__main__":
    print("Counting")
    df = pd.DataFrame(["a", "a", "a", "a", "b", "c"], columns=["val"])
    print("display(df):")
    show_all(df)
    df_pct = value_counts_pct(df.val)

    print()
    print("Normal distribution, check that bins catch everything")
    dist = np.random.normal(loc=0, scale=1, size=1000)

    bin_edges = make_bin_edges("-3 -2 ... 3")
    int_index, counted = bin_series(dist, bin_edges)
    counted_vc = counted.value_counts()
    apply_labelling(counted_vc, format_to_base_10, prefix="$")
    show_all(counted_vc)
