import math


def format_to_base_10(
    num, precision=2, suffixes=["", "k", "M", "G"], prefix="", trim_0_decimals=False
):
    """Turn 1_234_000 into 1.23M"""
    # TODO consider different suffixes, either a fixed set
    # or even a lookup with a dict and a nice label
    is_negative = num < 0
    num = abs(num)
    try:
        m = int(math.log10(num) // 3)
    except ValueError:
        # handle num of 0
        m = 0
    if is_negative:
        sgn = "-"
    else:
        sgn = ""
    if m >= 0:
        short_form = num / 1000.0 ** m
        short_form_template = f"{short_form:.{precision}f}"
        if precision > 0 and trim_0_decimals:
            if short_form == int(short_form):
                # no decimals
                short_form = int(short_form)
                short_form_template = f"{short_form}"
        output = sgn + prefix + short_form_template + f"{suffixes[abs(m)]}"
        # output = sgn + prefix + f'{num/1000.0**m:.{precision}f}{suffixes[abs(m)]}'
    else:
        # nasty hack to avoid pennies turning into kilo
        output = sgn + prefix + f"{num:.{precision}f}"
    return output


def test_format_to_base_10():
    assert format_to_base_10(1000, precision=0) == "1k"
    assert format_to_base_10(1000, prefix="£") == "£1.00k"  # NOTE this looks stupid!
    assert format_to_base_10(1000, prefix="£", trim_0_decimals=True) == "£1k"
    assert format_to_base_10(2_500_000, prefix="£", precision=1) == "£2.5M"
    assert format_to_base_10(-2_500_000, prefix="£", precision=1) == "-£2.5M"
    assert format_to_base_10(-2_000_000, prefix="£", precision=1) == "-£2.0M"
    assert (
        format_to_base_10(-2_000_000, prefix="£", precision=1, trim_0_decimals=True)
        == "-£2M"
    )
    assert format_to_base_10(2_000, prefix="£", precision=2) == "£2.00k"

    # what happens to 1, 0.1, 0.01?
    assert format_to_base_10(1, precision=0) == "1"
    assert format_to_base_10(0.1, precision=1) == "0.1"
    assert format_to_base_10(0.01, precision=2) == "0.01"
    assert format_to_base_10(1, precision=1) == "1.0"
    assert format_to_base_10(0.01, precision=1) == "0.0"
    assert (
        format_to_base_10(1000.1, precision=1) == "1.0k"
    )  # NOTE not sure I like this!
    # add a postfix too e.g. s or m


if __name__ == "__main__":
    print(format_to_base_10(-2_500_000, prefix="£", precision=1))
    print(format_to_base_10(-2_000_000, prefix="£", precision=1))
