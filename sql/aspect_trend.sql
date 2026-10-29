-- Quarter by quarter: what share of a product's reviews complain about one aspect.
-- Concepts: LEFT JOIN (keep quarters with zero complaints), date arithmetic, GROUP BY.
WITH family_reviews AS (
    SELECT
        r.review_id,
        strftime('%Y', r.review_date) || '-Q' || ((CAST(strftime('%m', r.review_date) AS INTEGER) + 2) / 3) AS quarter
    FROM reviews AS r
    JOIN products AS p ON p.product_id = r.product_id
    WHERE p.family = :family AND r.review_date IS NOT NULL
),
complaints AS (
    SELECT DISTINCT review_id
    FROM aspect_mentions
    WHERE aspect = :aspect AND neg_prob >= :threshold
)
SELECT
    f.quarter,
    COUNT(*)                                                    AS reviews,
    COUNT(c.review_id)                                          AS reviews_complaining,
    ROUND(100.0 * COUNT(c.review_id) / COUNT(*), 2)             AS pct_reviews_complaining
FROM family_reviews AS f
LEFT JOIN complaints AS c ON c.review_id = f.review_id
GROUP BY f.quarter
HAVING COUNT(*) >= :min_reviews
ORDER BY f.quarter;
