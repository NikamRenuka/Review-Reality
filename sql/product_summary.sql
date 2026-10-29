-- One row per product family: how many reviews, average stars,
-- and how often people were unhappy (1-2 stars).
-- Concepts: JOIN, GROUP BY, aggregate functions, CASE, HAVING.
SELECT
    p.family,
    p.category,
    COUNT(*)                                                    AS reviews,
    ROUND(AVG(r.rating), 2)                                     AS avg_rating,
    ROUND(100.0 * SUM(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative,
    ROUND(100.0 * SUM(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END) / COUNT(*), 1)  AS pct_five_star,
    ROUND(100.0 * AVG(r.recommends), 1)                         AS pct_recommend,   -- AVG ignores NULLs
    MIN(r.review_date)                                          AS first_review,
    MAX(r.review_date)                                          AS last_review
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
GROUP BY p.product_id
HAVING COUNT(*) >= :min_reviews
ORDER BY reviews DESC;
