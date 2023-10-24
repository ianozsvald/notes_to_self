import numpy as np
import pandas as pd
import pytest
from datetime import datetime

from simpler_pandas import (
    make_bin_edges,
    bin_series,
    apply_labelling,
    sanity_check,
    flatten_multiindex,
    display,
    label_interval,
    show_df_details,
    show_all,
    to_datetime_helper,
)
from labelling import format_to_base_10

# TODO value_counts_pct has no tests yet


def test_to_datetime_helper():
    res = to_datetime_helper(pd.Series(["Jan 2023", "Feb 2024"]))
    expected = [datetime(2023, 1, 1), datetime(2024, 2, 1)]
    assert (res == expected).all()

    # it is harder to do a comparison on a series as we can't also
    # compare a pd.NaT along with valid values, we need to use .isna()
    # so instead just check that this gives us 3 elements with 1 NaT
    res = to_datetime_helper(pd.Series(["Jan 2023", "Feb 2024", "xx"]))
    assert len(res) == 3
    assert res.isna().sum() == 1


def test_show_all(capsys):
    # TODO run coverage, currently we don't test everything
    df = pd.DataFrame({"a": [1, 2, 3]})
    show_all(df)
    captured = capsys.readouterr()
    assert "0  1" in captured.out


def test_show_df_details(capsys):
    # TODO capture more stdout and check I agree
    # this will also flag if a future Pandas version changes their internals!
    # Example output would be like
    # 'is view False, is consolidated True, single block True, numeric mixed True\n1 blocks looking like:\n(NumericBlock: ...
    df = pd.DataFrame({"a": [1, 2, 3]})
    show_df_details(df)
    captured = capsys.readouterr()
    assert "is view False" in captured.out
    assert "is consolidated True, single block True" in captured.out


# TODO replace with warns check https://docs.pytest.org/en/latest/how-to/capture-warnings.html#warns
def test_sanity_check():
    df = pd.DataFrame({" a": [1, 2], "b": [3, 4], "c ": [5, 6]})
    # the warns test fails - why?
    # with pytest.warns(Warning,  match='Weirdness for column 0 with " a"'):
    #    sanity_check(df)
    with pytest.raises(Warning):
        sanity_check(df)
    df = pd.DataFrame({"Timestamp\xa0": [1, 2]})
    with pytest.raises(Warning):
        sanity_check(df)
    df = pd.DataFrame({"Timestamp\xa0value": [1, 2]})
    with pytest.raises(Warning):
        sanity_check(df)


def test_flatten_multiindex():
    # TODO need to make a dual multiindex test
    df = pd.DataFrame({"a": ["a", "a", "b", "b"], "b": [0, 1, 2, 3], "c": [6, 7, 8, 9]})
    # flatten multiindex on index
    df_flattened = flatten_multiindex(df.set_index(["a", "b"]), on="index")
    assert df_flattened.index[0] == "a_0"
    assert df_flattened.index[3] == "b_3"
    # do the same automatically
    df_flattened = flatten_multiindex(df.set_index(["a", "b"]))
    assert df_flattened.index[0] == "a_0"
    assert df_flattened.index[3] == "b_3"

    # do the same on columns
    df_flattened = flatten_multiindex(df.set_index(["a", "b"]).T, on="columns")
    assert df_flattened.columns[0] == "a_0"
    assert df_flattened.columns[3] == "b_3"

    # detect columns automatically
    df_flattened = flatten_multiindex(df.set_index(["a", "b"]).T)
    assert df_flattened.columns[0] == "a_0"
    assert df_flattened.columns[3] == "b_3"


def test_make_bin_edges():
    bins = make_bin_edges("1 2 ... 5")
    assert (bins == np.array([-np.inf, 1, 2, 3, 4, 5, np.inf])).all()
    bins = make_bin_edges("-5 -3 ... 5")
    assert (bins == np.array([-np.inf, -5, -3, -1, 1, 3, 5, np.inf])).all()
    bins = make_bin_edges("-0.5 -0.4 ... -0.3")
    np.testing.assert_allclose(bins, np.array([-np.inf, -0.5, -0.4, -0.3, np.inf]))
    bins = make_bin_edges("-0.5 -0.4 ... 0.1")
    np.testing.assert_allclose(
        bins,
        np.array([-np.inf, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, np.inf]),
        atol=1e-5,
    )
    bins = make_bin_edges("0.0 0.1 ... 0.5")
    np.testing.assert_allclose(
        bins, np.array([-np.inf, 0, 0.1, 0.2, 0.3, 0.4, 0.5, np.inf]), atol=1e-5
    )
    bins = make_bin_edges("0.5 0.4 ... 0.0")
    np.testing.assert_allclose(
        bins, np.array([np.inf, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -np.inf]), atol=1e-5
    )
    bins = make_bin_edges("0.5 0.4 ... 0.0", left_inf=False, right_inf=False)
    np.testing.assert_allclose(
        bins, np.array([0.5, 0.4, 0.3, 0.2, 0.1, 0.0]), atol=1e-5
    )


def test_bin_series():
    dist = np.array([-100, 0, 5])
    bin_edges = [-np.inf, -1000, 0, 1000]
    counted = bin_series(dist, bin_edges)
    assert (counted.value_counts().values == np.array([0, 1, 2])).all()
    display(counted.value_counts().sort_index(ascending=True))


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


def test_apply_labelling():
    items = [
        1,
        1,
        1,
        2,
        3,
    ]
    # df = pd.DataFrame({"items": items})
    bin_edges = make_bin_edges("0 1 ... 2")
    counted = bin_series(items, bin_edges)
    vc = counted.value_counts()
    vc.index = apply_labelling(vc.index, format_to_base_10, prefix="", precision=0)
    assert vc.index[0] == "< 0"
    assert (vc.index == ["< 0", "[0 - 1)", "[1 - 2)", ">= 2"]).all()
    assert (vc.values == [0, 0, 3, 2]).all()

    items = [0.0, 0.5, 0.99, 1.0]
    # df = pd.DataFrame({"pct": items})
    bin_edges = make_bin_edges("0.0 0.1 ... 1.0", left_inf=False)
    counted = bin_series(items, bin_edges)
    vc = counted.value_counts()
    print(vc)  # before formatting
    vc.index = apply_labelling(vc.index, format_to_base_10, prefix="", precision=1)
    print(vc)  # after formatting
    assert (vc.index[:2] == ["[0.0 - 0.1)", "[0.1 - 0.2)"]).all()
    assert (vc.index[3:4] == ["[0.3 - 0.4)"]).all()


def test_apply_labelling_percent():
    items = [0, 0.1, 0.8, 0.99, 1.0]
    df = pd.DataFrame({"items": items})
    bin_edges = make_bin_edges("0 0.2 ... 1.0")
    counted = bin_series(items, bin_edges)
    vc = counted.value_counts()
    vc.index = apply_labelling(vc.index, format_to_base_10, prefix="", precision=1)
    print(vc)
    assert vc.index[0] == "< 0.0"
    assert (
        vc.index
        == [
            "< 0.0",
            "[0.0 - 0.2)",
            "[0.2 - 0.4)",
            "[0.4 - 0.6)",
            "[0.6 - 0.8)",
            "[0.8 - 1.0)",
            ">= 1.0",
        ]
    ).all()
    assert (vc.values == [0, 2, 0, 0, 0, 2, 1]).all()

    items = [0, 10, 80, 99, 100]
    # df = pd.DataFrame({"items": items})
    bin_edges = make_bin_edges("0 20 ... 100")
    counted = bin_series(items, bin_edges)
    vc = counted.value_counts()
    vc.index = apply_labelling(
        vc.index, format_to_base_10, prefix="", postfix="%", precision=0
    )
    print(vc)
    assert (
        vc.index
        == [
            "< 0%",
            "[0% - 20%)",
            "[20% - 40%)",
            "[40% - 60%)",
            "[60% - 80%)",
            "[80% - 100%)",
            ">= 100%",
        ]
    ).all()
