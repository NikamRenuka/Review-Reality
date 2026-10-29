-- Days when a product got far more reviews than it usually does.
-- A burst is NOT proof of fake reviews (a sale or a holiday can cause one);
-- it is a pattern worth a closer look.
-- Concepts: CTE (WITH), window functions (AVG ... OVER PARTITION BY), filtering on a ratio.
WITH daily AS (
    SELECT
        r.product_id,
        r.review_date                 AS day,
        COUNT(*)                      AS reviews,
        ROUND(AVG(r.rating), 2)       AS avg_rating
    FROM reviews AS r
    WHERE r.review_date IS NOT NULL
    GROUP BY r.product_id, r.review_date
),
with_typical AS (
    SELECT
        d.*,
        AVG(d.reviews) OVER (PARTITION BY d.product_id) AS typical_daily_reviews
    FROM daily AS d
)
SELECT
    p.family,
    w.day,
    w.reviews,
    w.avg_rating,
    ROUND(w.typical_daily_reviews, 1)              AS typical_daily_reviews,
    ROUND(w.reviews / w.typical_daily_reviews, 1)  AS times_typical
FROM with_typical AS w
JOIN products AS p ON p.product_id = w.product_id
WHERE w.reviews >= :min_reviews
  AND w.reviews >= :min_ratio * w.typical_daily_reviews
  AND (:family IS NULL OR p.family = :family)
ORDER BY times_typical DESC, w.reviews DESC;
