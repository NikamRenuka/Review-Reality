-- One row per product family: star rating next to how many reviews contain
-- at least one complaint sentence, plus the most complained-about aspect.
-- Concepts: several CTEs, a window function (ROW_NUMBER) to pick the top aspect, LEFT JOINs.
WITH complaint_reviews AS (
    SELECT DISTINCT review_id
    FROM aspect_mentions
    WHERE neg_prob >= :threshold
),
aspect_counts AS (
    SELECT
        r.product_id,
        m.aspect,
        COUNT(DISTINCT m.review_id) AS reviews_complaining,
        ROW_NUMBER() OVER (PARTITION BY r.product_id ORDER BY COUNT(DISTINCT m.review_id) DESC) AS rank
    FROM aspect_mentions AS m
    JOIN reviews AS r ON r.review_id = m.review_id
    WHERE m.neg_prob >= :threshold
    GROUP BY r.product_id, m.aspect
)
SELECT
    p.family,
    p.category,
    COUNT(*)                                                    AS reviews,
    ROUND(AVG(r.rating), 2)                                     AS avg_rating,
    ROUND(100.0 * SUM(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative,
    ROUND(100.0 * COUNT(c.review_id) / COUNT(*), 1)             AS pct_with_complaint,
    a.aspect                                                    AS top_complaint
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
LEFT JOIN complaint_reviews AS c ON c.review_id = r.review_id
LEFT JOIN aspect_counts AS a ON a.product_id = r.product_id AND a.rank = 1
GROUP BY p.product_id
HAVING COUNT(*) >= :min_reviews
ORDER BY reviews DESC;
