"""Calculate and estimate 95th CI bounds for a binary value"""
import numpy as np

# TODO
# add test for both, same arr, check for outer likely bounds
# 95th > 5th etc

rng = np.random.default_rng()


def calculate_ci(arr):
    p = arr.mean()
    q = 1-p
    n = arr.shape[0]
    # 1.96 yields 95th CI (not 95.4th)
    se_95 = np.sqrt((p * q) / n) * 1.96
    print(f"mean {p:0.3f}, 2.5th CI {p-se_95:0.3f}, 97.5th CI {p+se_95:0.3f}")
    return p-se_95, p, p+se_95
    

def calculate_bookstrap_ci(arr, repeats=1000):
    """Build repeats' worth of bootstrap samples, calculate percentiles"""
    pc2_5_idx = int(repeats * 0.025)
    pc50_idx = int(repeats * 0.5)
    pc97_5_idx = int(repeats * 0.975)
    percentiles = (np.array([0.025, 0.5, 0.975]) * repeats).astype(int)
    n = arr.shape[0]
    means = []
    for it in range(repeats):
        mask = rng.integers(0, n, n)
        arr2 = arr[mask]
        means.append(arr2.mean())
    means = np.array(means)
    means.sort()
    print(f"Bootstrap mean {means[pc50_idx]:0.3f}, 2.5th CI {means[pc2_5_idx]:0.3f}, 97.5th CI {means[pc97_5_idx]:0.3f}")
    return means[percentiles]


if __name__ == "__main__":
    arr = rng.binomial(1, 0.5, 1000)
    arr = arr < 0.01
    print(calculate_ci(arr))
    print(calculate_bookstrap_ci(arr))

