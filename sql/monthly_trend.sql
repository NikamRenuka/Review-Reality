-- Month-by-month review volume, average stars and share of unhappy reviews
-- for one product family (or all when :family is NULL).
-- Concepts: date functions (strftime), GROUP BY on a calculated column.
SELECT
    strftime('%Y-%m', r.review_date)                                AS month,
    COUNT(*)                                                        AS reviews,
    ROUND(AVG(r.rating), 2)                                         AS avg_rating,
    ROUND(100.0 * SUM(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
WHERE r.review_date IS NOT NULL
  AND (:family IS NULL OR p.family = :family)
GROUP BY month
ORDER BY month;
