from functools import partial
import pandas as pd
import numpy as np
from IPython.display import display
from simpler.labelling import format_to_base_10

# make_bin_edges will turn e.g. "1 2 ... 10" into [-inf, 1, 2, ..., 9, 10, inf]
# bin_series will take the bin edges and a series and put them into bins
# apply_labelling will format any series
# see example in __main__

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


def to_datetime_helper(ser, format="%b %Y", trim_at=10):
    """Show conversion errors (as NaT) from original strings during `to_datetime` conversion
    A `format` of `%b %Y` corresponds to e.g. 'Jan 2023'
    `to_datetime` seems to skip whitespace"""
    ser_nat = pd.to_datetime(ser, errors="coerce", format=format)
    # ser_nat can have NaT if error occurred
    mask = ser_nat.isna()
    print(f"{mask.sum()} errors seen in conversion")
    # show the errors, trim if there are too many to show
    mask_cum = mask.cumsum()
    if mask.sum() > trim_at:
        print(f"{mask.sum()} is too many errors, trimming to {trim_at}")
    mask[mask_cum > trim_at] = False  # get the items up until the trim point
    for idx, value in ser[mask].items():
        print(f"Row {idx} '{value}'")
    return ser_nat


def check_series_is_ordered(ser, ascending=True):
    """Check 1 series is ascending"""
    assert ascending == True, "Haven't done descending yet, nor tested this"
    return (
        ser.shift()[1:].reset_index(drop=True) >= ser[:-1].reset_index(drop=True)
    ).all()


def show_df_details(df):
    """Dig into _data hidden attribute, note is_consolidated check can be slow first time"""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # 2023 we get DeprecationWarning: DataFrame._data is deprecated and will be removed in a future version. Use public APIs instead.
        print(
            f"""is view {df._data.is_view}, is consolidated {df._data.is_consolidated()}, single block {df._data.is_single_block}"""
        )
        print(f"""{df._data.nblocks} blocks looking like:""")
        print(df._data.blocks)


def sanity_check(df):
    """Raise warnings if weirdness found"""
    # TODO could consider using unidecode to check for weirdness
    # TODO for object cols apply same sanity checks
    # check for strange things in columns
    for n, item in enumerate(df.columns):
        weird = False
        if item != item.strip():
            # check for whitespace at start or end of column entry
            weird = True
        if "\xa0" in item:
            # check for non-breaking space
            weird = True
        if weird:
            raise Warning(f'Weirdness for column {n} with value "{item}"')


def show_all(x, head=999, tail=10):
    """List more rows of DataFrame and Series results than usual"""
    # CONSIDER using 'display.max_columns' too?
    from IPython.display import display

    head = min(x.shape[0], head)
    tail = min(x.shape[0] - head, tail)

    if head > 0:
        with pd.option_context("display.max_rows", None):
            display(x.head(head))
    if tail > 0:
        if head > 0:
            print("...")
        with pd.option_context("display.max_rows", None):
            display(x.tail(tail))


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
# https://github.com/dexplo/minimally_sufficient_pandas/blob/master/minimally_sufficient_pandas/_pandas_accessor.py#L42
def flatten_multiindex(df, on=None):
    """Flatten MultiIndex to flat index after e.g. groupby, on can be automatic (None) or index or columns"""
    df = df.copy()
    if on is None:
        index = hasattr(df.index, "levels")
        columns = hasattr(df.columns, "levels")
    else:
        index = on == "index" or on == "both"
        columns = on == "columns" or on == "both"
    if index is True:
        new_flat_index = [
            "_".join(str(s) for s in multi_index) for multi_index in df.index.values
        ]
        df.index = new_flat_index
    if columns is True:
        new_flat_index = [
            "_".join(str(s) for s in multi_index) for multi_index in df.columns.values
        ]
        df.columns = new_flat_index
    return df


def make_bin_edges(desc, left_inf=True, right_inf=True):
    """Given bin description (e.g. "1 2 ... 10") make a sequence bounded by Infs

    desc=='0 1 ... 5' -> [-np.inf, 0, 1, 2, 3, 4, 5, np.inf]
    desc=='5 4 ... 0' -> [np.inf, 5, 4, 3, 2, 1, 0, -np.inf]
    desc=='5 4 ... 0' -> [5, 4, 3, 2, 1, 0] if left_inf==right_inf==False"""
    parts = desc.split(" ")
    # hopefully we have floats, if not this will just die
    start = float(parts[0])
    step = float(parts[1]) - float(parts[0])
    end = float(parts[3])
    num = round((end - start) / step) + 1
    # print(start, end, step, num)
    bins = np.linspace(start, end, num=num)

    # concatenate infs (if needed) and the calculated bins
    items = []
    left_inf_val, right_inf_val = -np.inf, np.inf
    if step < 0:
        # if step is descending we have to make left-inf large and right-inf small
        left_inf_val, right_inf_val = np.inf, -np.inf
    if left_inf:
        items.append([left_inf_val])
    items.append(bins)
    if right_inf:
        items.append([right_inf_val])
    bins = np.concatenate(items)

    return bins


def bin_series(dist, bin_edges):
    """Bin a series using specified bin_edges"""
    interval_index = pd.IntervalIndex.from_breaks(bin_edges, closed="left")
    binned = pd.cut(dist, interval_index)
    return binned


# TODO make right-closed too
def label_interval(interval, format_fn=None, **kwargs):
    """Internal function to make a friendly human interval label e.g. [-1 - 0)"""
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


def apply_labelling(ser, format_fn=None, **kwargs):
    """Modify index using labelling function"""
    label_interval_args = partial(label_interval, format_fn=format_fn, **kwargs)
    new_index = ser.map(label_interval_args)
    return new_index


if __name__ == "__main__":
    print("Counting")
    df = pd.DataFrame(["a", "a", "a", "a", "b", "c"], columns=["val"])
    print("display(df):")
    show_all(df)
    df_pct = value_counts_pct(df.val)

    print()
    print("Normal distribution, check that bins catch everything")
    dist = np.random.normal(loc=0, scale=1, size=1000)

    counted = bin_series(dist, make_bin_edges("-3 -2 ... 3"))
    counted_vc = counted.value_counts()
    counted_vc.index = apply_labelling(counted_vc.index, format_to_base_10, prefix="$")
    show_all(counted_vc)

    show_df_details(df)
