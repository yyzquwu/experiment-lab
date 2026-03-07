from exp.power import binary_sample_size_per_variant, mde_binary, mde_continuous


def test_sample_size_and_mde_relationship() -> None:
    baseline = 0.10
    n = binary_sample_size_per_variant(baseline_rate=baseline, mde_absolute=0.01, alpha=0.05, power=0.8)
    assert n > 1000

    mde = mde_binary(baseline_rate=baseline, n_per_variant=n, alpha=0.05, power=0.8)
    assert 0.007 <= mde <= 0.013


def test_continuous_mde_shrinks_with_more_data() -> None:
    small = mde_continuous(sigma=12.0, n_per_variant=1000)
    large = mde_continuous(sigma=12.0, n_per_variant=4000)
    assert large < small
