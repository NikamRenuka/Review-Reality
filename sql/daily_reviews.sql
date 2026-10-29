-- Reviews per day for one product family (used to draw the review-activity timeline).
SELECT
    r.review_date           AS day,
    COUNT(*)                AS reviews,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
WHERE p.family = :family AND r.review_date IS NOT NULL
GROUP BY r.review_date
ORDER BY r.review_date;
