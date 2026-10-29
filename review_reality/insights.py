"""Turn calculated tables into short findings for the dashboard.

Nothing here is typed by hand: each function searches the real numbers and
returns None when the data does not support a finding.
"""
from itertools import combinations


def similar_stars_biggest_gap(products, max_star_diff=0.05, min_gap=1.0):
    """Among products whose average stars differ by at most `max_star_diff`,
    find the pair with the biggest difference in % of reviews with a complaint.

    `products` needs columns: family, avg_rating, pct_with_complaint.
    Returns a dict, or None if no pair differs by at least `min_gap` points.
    """
    best = None
    for (_, a), (_, b) in combinations(products.iterrows(), 2):
        if abs(a["avg_rating"] - b["avg_rating"]) > max_star_diff:
            continue
        gap = abs(a["pct_with_complaint"] - b["pct_with_complaint"])
        if gap >= min_gap and (best is None or gap > best["gap"]):
            more, fewer = (a, b) if a["pct_with_complaint"] > b["pct_with_complaint"] else (b, a)
            best = {
                "more": more["family"], "more_stars": more["avg_rating"], "more_pct": more["pct_with_complaint"],
                "fewer": fewer["family"], "fewer_stars": fewer["avg_rating"], "fewer_pct": fewer["pct_with_complaint"],
                "gap": round(gap, 1),
            }
    return best


def group_similar(pairs):
    """Join linked pairs into groups: if A~B and B~C, then A, B and C form one group.

    `pairs` needs columns review_id_a, review_id_b. Returns a list of sets of review ids,
    largest group first. (This is "union-find": each id points to a group leader.)
    """
    leader = {}

    def find(x):
        leader.setdefault(x, x)
        while leader[x] != x:
            leader[x] = leader[leader[x]]
            x = leader[x]
        return x

    for a, b in zip(pairs["review_id_a"], pairs["review_id_b"]):
        leader[find(a)] = find(b)
    groups = {}
    for x in list(leader):
        groups.setdefault(find(x), set()).add(x)
    return sorted(groups.values(), key=lambda g: (-len(g), min(g)))


def biggest_aspect_difference(aspects_a, aspects_b, min_gap=0.5):
    """Which aspect differs most between two products (in % of reviews complaining)?

    Aspects missing for one product count as 0%. Returns (aspect, pct_a, pct_b) or None.
    """
    a = dict(zip(aspects_a["aspect"], aspects_a["pct_reviews_complaining"]))
    b = dict(zip(aspects_b["aspect"], aspects_b["pct_reviews_complaining"]))
    best = None
    for aspect in sorted(set(a) | set(b)):
        pa, pb = a.get(aspect, 0.0), b.get(aspect, 0.0)
        if abs(pa - pb) >= min_gap and (best is None or abs(pa - pb) > abs(best[1] - best[2])):
            best = (aspect, pa, pb)
    return best
