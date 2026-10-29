import pandas as pd

from review_reality.insights import biggest_aspect_difference, group_similar, similar_stars_biggest_gap


def test_group_similar_joins_linked_pairs():
    pairs = pd.DataFrame({"review_id_a": [1, 2, 7, 10], "review_id_b": [2, 3, 8, 1]})
    assert group_similar(pairs) == [{1, 2, 3, 10}, {7, 8}]


def test_group_similar_empty():
    assert group_similar(pd.DataFrame({"review_id_a": [], "review_id_b": []})) == []


def test_similar_stars_biggest_gap_picks_closest_stars_with_largest_gap():
    products = pd.DataFrame({
        "family": ["Tablet", "Batteries", "Speaker", "Reader"],
        "avg_rating": [4.47, 4.45, 4.65, 4.20],
        "pct_with_complaint": [5.7, 8.8, 3.0, 20.0],
    })
    found = similar_stars_biggest_gap(products)
    # Reader has the biggest complaint rate but its stars are not within 0.05 of anything.
    assert (found["more"], found["fewer"], found["gap"]) == ("Batteries", "Tablet", 3.1)


def test_similar_stars_biggest_gap_returns_none_when_nothing_qualifies():
    products = pd.DataFrame({"family": ["A", "B"], "avg_rating": [4.0, 4.5], "pct_with_complaint": [1.0, 9.0]})
    assert similar_stars_biggest_gap(products) is None


def test_biggest_aspect_difference_counts_missing_aspects_as_zero():
    a = pd.DataFrame({"aspect": ["Battery life", "Price & value"], "pct_reviews_complaining": [5.3, 2.0]})
    b = pd.DataFrame({"aspect": ["Price & value"], "pct_reviews_complaining": [1.8]})
    assert biggest_aspect_difference(a, b) == ("Battery life", 5.3, 0.0)


def test_biggest_aspect_difference_ignores_tiny_gaps():
    a = pd.DataFrame({"aspect": ["Screen & display"], "pct_reviews_complaining": [0.8]})
    b = pd.DataFrame({"aspect": ["Screen & display"], "pct_reviews_complaining": [0.6]})
    assert biggest_aspect_difference(a, b) is None
