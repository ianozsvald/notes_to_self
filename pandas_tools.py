import pandas as pd
import numpy as np
from IPython.display import display

dayofweek_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}


# TODO
# bin to include NaN <NA> as an extra bin, maybe optional?
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



def bin_and_label(dist, bin_edges):
    indices = np.arange(0, len(bin_edges)+1, 1)
    #print(f"indices {indices}")
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
    assert counted.sum() == len(dist), (len(counted), counted.sum(), len(dist))
    return counted
   

def test_bin_and_label():
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


if __name__ == "__main__":
    print("Counting")
    df = pd.DataFrame(['a', 'a', 'a', 'a', 'b', 'c'], columns=['val'])
    df_pct = value_counts(df.val)

    print()
    print("Normal distribution, check that bins catch everything")
    dist = np.random.normal(loc=0, scale=1, size=1000)
    bin_edges = [-3, -2, -1, 0, 1, 2, 3]
    counted = bin_and_label(dist, bin_edges)
    print(counted)
