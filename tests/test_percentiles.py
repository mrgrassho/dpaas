from dpaas_core.percentiles import PercentileMatcher


def test_percentile_month_matching_for_weight_range():
    matcher = PercentileMatcher()
    matches = matcher.as_month_map(5.0, 7.5)

    assert matches["girls"]["P50"] == [2, 3, 4, 5, 6]
    assert matches["boys"]["P50"] == [2, 3, 4, 5]


def test_percentile_open_ended_max():
    matcher = PercentileMatcher()
    matches = matcher.match(17.0, None)

    assert matches
    assert all(match.weight_kg >= 17.0 for match in matches)
