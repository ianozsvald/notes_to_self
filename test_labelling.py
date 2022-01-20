from labelling import format_to_base_10


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

    # TODO add a postfix too e.g. s or m
    assert format_to_base_10(1, precision=0, postfix="%") == "1%"
    assert format_to_base_10(-1, precision=0, postfix="%") == "-1%"
    assert format_to_base_10(0.1, precision=1, postfix="%") == "0.1%"
