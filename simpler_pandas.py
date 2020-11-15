import pandas as pd
import numpy as np
from IPython.display import display
import pytest
from labelling import format_to_base_10


# GroupBy notes
# dfs.groupby([dfs.date.dt.year]) # can group on Series rather than name

# for Pandas mapping of .dt.dayofweek to a nice name
dayofweek_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}


def show_all(x, nbr_rows=999):
    '''List more rows of DataFrame and Series results than usual'''
    from IPython.display import display
    with pd.option(context('display.max_rows', nbr_rows)):
        display(x)


# TODO 
# check value_counts in a Notebook with use_display=True
def value_counts(ser, rows=10, use_display=False):
    """Prettier value counts, returns dataframe of counts & percents"""
    vc1 = ser.value_counts(dropna=False)
    vc2 = ser.value_counts(dropna=False, normalize=True)
    df = pd.DataFrame({'count': vc1, 'pct': vc2 * 100})
    df['pct_cum'] = df.pct.cumsum()
    if use_display:
        # use style as that's CSS/HTML only for a Notebook
        display(df[:rows].style.format({'pct': '{:0.1f}%'}))
    else:
        formatters = {'pct': '{:0.1f}%'.format, 'pct_cum': '{:0.1f}%'.format}
        print(df.to_string(formatters=formatters))
    rows_not_shown = max(df.shape[0]-rows, 0)
    print(f'Total rows not shown {rows_not_shown} of {df.shape[0]}')
    return df


# TODO test for empty bin_edges case
# TODO consider making <0 optional
# TODO bin to include NaN <NA> as an extra bin, maybe optional?
def bin_and_labelXX(dist, bin_edges, count_nan=False, count_inf=False):
    """Bin items into discrete ranges
    right is closed by default so bins are [lower, upper)
    By default NaN and Inf and -Inf are counted in the highest bin
    """
    if np.isinf(dist).any() and count_inf:
        raise ValueError('This code does not handle Infs separately yet')
    if np.isnan(dist).any() and count_nan:
        raise ValueError('This code does not handle Nulls separately yet')
    indices = np.arange(0, len(bin_edges)+1, 1)
    ser_binned = pd.Series(np.digitize(dist, bin_edges))
    labels = []
    labels.append(f'<{bin_edges[0]}')
    previous = bin_edges[0]
    item="NOTASSIGNED" # error condition if only 1 bin edge to solve (see unit test)
    for idx, item in enumerate(bin_edges[1:]):
        labels.append(f'[{previous} - {item})')
        previous = item
    labels.append(f'>={item}')
    #print(f"bin_edges: {bin_edges}")
    #print(f"labels: {labels}")
    dict_labels = {n:label for (n, label) in enumerate(labels)}
    counted = ser_binned.value_counts().reindex(indices).fillna(0).sort_index().rename(dict_labels)
    # check we aren't losing any items
    assert counted.sum() == len(dist), (len(counted), counted.sum(), len(dist))
    return counted
   

def XXtest_bin_and_label():
    # check that out of order items and a gap are counted appropriately
    dist = [4, -1, 0, 0, 0, 1, 2, 8, 9, 10]
    bin_edges = np.arange(2, 10, 2)
    counted = bin_and_label(dist, bin_edges)
    expected = pd.Series([5., 1., 1., 0., 3.], index=['<2', '[2 - 4)', '[4 - 6)', '[6 - 8)', '>=8'])
    assert expected.sum() == len(dist), "We seem to have lost at least one item"
    assert (counted == expected).all()

    dist = [0, 0, 0, 1, 100]
    bin_edges = [1, 2]
    counted = bin_and_label(dist, bin_edges)
    expected = pd.Series([3, 1, 1], index=['<1', '[1 - 2)', '>=2'])
    assert expected.sum() == len(dist), "We seem to have lost at least one item"
    assert (counted == expected).all()

    # TODO test for only 1 bin edge

def XXtest_bin_and_label_inf_nan():
    '''Check np.inf and np.nan in bin_and_label'''
    dist = np.array([np.nan, np.inf, -1, 0, 1, 2, 3])
    bin_edges = np.array([0, 1, 2])
    counts = bin_and_label(dist, bin_edges)
    print(counts)

    with pytest.raises(ValueError):
        counts = bin_and_label(dist, bin_edges, count_nan=True)
    with pytest.raises(ValueError):
        counts = bin_and_label(dist, bin_edges, count_inf=True)

#TODO add test
def flatten_multiindex(gpby, index=True, columns=True):
    '''Flatten MultiIndex to flat index after e.g. groupby'''
    if index is True:
        new_flat_index = ['_'.join(str(s) for s in multi_index) for multi_index in gpby.index.values]
        #gpby = gpby.reset_index(drop=True)
        gpby.index = new_flat_index
    if columns is True:
        new_flat_index = ['_'.join(str(s) for s in multi_index) for multi_index in gpby.columns.values]
        #gpby = gpby.reset_index(drop=True)
        gpby.columns = new_flat_index
    return gpby


# TODO add test
# TODO let me label <= >= for the extremes, maybe let me make a nice range with a convenience fist?
# int_index._data.to_numpy()[0] this gives Interval items, maybe I need to override this somehow to build a better display?
# pandas._libs.interval.Interval from type(int_index._data.to_numpy()[0])
def bin_and_label(dist, bin_edges):
    int_index = pd.IntervalIndex.from_breaks(bin_edges, closed='left')
    cat = pd.cut(dist, int_index)
    return int_index, cat

def test_bin_and_label():
    dist = np.array([-100, 0, 5])
    bin_edges = [-np.inf, -1000, 0, 1000]
    int_index, counted = bin_and_label(dist, bin_edges)
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
            label = f'< {right}'
        elif np.isinf(interval.right):
            label = f'>= {left}'
        else:
            label = f'[{left} - {right})' 

    return label

def test_label_interval():
    bin_edges = [-np.inf, -1000, 0, np.inf]
    int_index = pd.IntervalIndex.from_breaks(bin_edges, closed='left')
    interval = int_index._data.to_numpy()[0] # Interval(-inf, -1000.0, closed='left')
    assert label_interval(interval) == '< -1000.0'
    interval = int_index._data.to_numpy()[1] # Interval(-1000.0, 0.0, closed='left')
    assert label_interval(interval) == '[-1000.0 - 0.0)'
    interval = int_index._data.to_numpy()[2] # Interval(0.0, 1000.0, closed='left')
    assert label_interval(interval) == '>= 0.0'

    interval = int_index._data.to_numpy()[0] 
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True) == '< -1k'
    interval = int_index._data.to_numpy()[1] 
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True) == '[-1k - 0)'
    interval = int_index._data.to_numpy()[2] 
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True) == '>= 0'

    interval = int_index._data.to_numpy()[0] 
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True, prefix="£") == '< -£1k'
    interval = int_index._data.to_numpy()[1] 
    assert label_interval(interval, format_to_base_10, trim_0_decimals=True, prefix="£") == '[-£1k - £0)'

if __name__ == "__main__":
    print("Counting")
    df = pd.DataFrame(['a', 'a', 'a', 'a', 'b', 'c'], columns=['val'])
    print('display(df):')
    display(df)
    df_pct = value_counts(df.val)

    print()
    print("Normal distribution, check that bins catch everything")
    dist = np.random.normal(loc=0, scale=1, size=1000)
    #bin_edges = [-3, -2, -1, 0, 1, 2, 3]
    #counted = bin_and_label(dist, bin_edges)
    #display(counted)

    bin_edges = [-np.inf, -3, -2, -1, 0, 1, 2, 3, np.inf]
    int_index, counted2 = bin_and_label(dist, bin_edges)
    #display(counted2)
    display(counted2.value_counts().sort_index(ascending=True))