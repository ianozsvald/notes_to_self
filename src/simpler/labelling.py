"""Text labelling helpers"""

import math


def format_to_base_10(
    num,
    precision=2,
    suffixes=["", "k", "M", "G"],
    prefix="",
    postfix="",
    trim_0_decimals=False,
):
    """Turn 1_234_000 into 1.23M"""
    # TODO consider different suffixes, either a fixed set
    # or even a lookup with a dict and a nice label
    is_negative = num < 0
    num = abs(num)
    try:
        # test if we have 3+ digit mantissa
        m = int(math.log10(num) // 3)
    except ValueError:
        # handle num of 0
        m = 0
    if is_negative:
        sgn = "-"
    else:
        sgn = ""
    if m >= 0:
        short_form = num / 1000.0**m
        short_form_template = f"{short_form:.{precision}f}"
        if precision > 0 and trim_0_decimals:
            if short_form == int(short_form):
                # no decimals
                short_form = int(short_form)
                short_form_template = f"{short_form}"
        output = sgn + prefix + short_form_template + f"{suffixes[abs(m)]}" + postfix
        # output = sgn + prefix + f'{num/1000.0**m:.{precision}f}{suffixes[abs(m)]}'
    else:
        # nasty hack to avoid pennies turning into kilo
        output = sgn + prefix + f"{num:.{precision}f}" + postfix
    return output


if __name__ == "__main__":
    print(format_to_base_10(-2_500_000, prefix="£", precision=1))
    print(format_to_base_10(-2_000_000, prefix="£", precision=1))
