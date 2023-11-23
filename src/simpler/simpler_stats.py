"""Calculate and estimate 95th CI bounds for a binary value"""
import numpy as np

# WARNING
# THIS IS ALL VERY ALPHA CODE, IT NEEDS SORTING OUT!

# binomial test for no-successes by random sampling
# sum(np.random.binomial(9, 0.1, 20000) == 0)/20000. # given 9 cold sales calls with a 10% chance of success, what's the chance that all 9 had no success? 38%

# TODO
# add test for both, same arr, check for outer likely bounds
# 95th > 5th etc

rng = np.random.default_rng()

# NOTE these are hardcoded to certain ranges, need to simplify this
# so calculate_ci generates a 1se (not 95th percentile) interval
# and calculate_bootstrap_ci gives any requested percentiles


def calculate_ci(arr):
    """Calculate a 90% CI"""
    p = arr.mean()
    q = 1 - p
    n = arr.shape[0]
    # 1.96 yields 95th CI (not 95.4th)
    se_95 = np.sqrt((p * q) / n) * 1.96
    print(f"mean {p:0.3f}, 2.5th CI {p-se_95:0.3f}, 97.5th CI {p+se_95:0.3f}")
    return p - se_95, p, p + se_95


def calculate_bootstraps(arr, repeats=1000, agg_fn=np.sum):
    """Calculate a bootstrap statistic (default `sum`)
    Given an array calculate `repeats` bootstrap samples
    taking the `agg_fn` of each and return `repeats` results"""
    n = arr.shape[0]
    aggs = []
    for it in range(repeats):
        mask = rng.integers(0, n, n)
        aggs.append(agg_fn(arr[mask]))
    aggs = np.array(aggs)
    return aggs


def calculate_bootstrap_ci(
    arr, percentiles=[0.025, 0.5, 0.975], repeats=1000, agg_fn=np.mean
):
    """Bootstrap CI
    Given percentiles, calculate a repeated statistic (default is the mean) on the bootstrap
    and return the values at the matching percentiles"""
    perc = np.array([int(p * repeats) for p in percentiles])
    aggs = calculate_bootstrap(arr, repeats, agg_fn)
    aggs.sort()
    return aggs[perc]


def test_calculate_bootstrap():
    arr = np.ones(10)
    bootstraps = calculate_bootstraps(arr, repeats=10_000)
    # given 10 * 1 in arr, we expect 10 as the result (no variance)
    np.testing.assert_equal(bootstraps[0], 10)
    assert np.var(bootstraps) == 0, "Not expecting any variance"
    assert bootstraps.shape == (10_000,)

    HIGH = 100
    SIZE = 100
    arr = np.random.randint(0, high=HIGH, size=SIZE)
    bootstraps = calculate_bootstraps(arr, repeats=1_000, agg_fn=np.sum)
    assert bootstraps.min() >= 0
    assert bootstraps.max() <= SIZE * HIGH
    bootstraps = calculate_bootstraps(arr, repeats=1_000, agg_fn=np.mean)
    assert bootstraps.min() >= 0
    assert bootstraps.max() <= SIZE


if __name__ == "__main__":
    arr = rng.binomial(1, 0.5, 1000)
    arr = arr < 0.01
    print(calculate_ci(arr))
    print(calculate_bootstrap_ci(arr, repeats=10_000))
