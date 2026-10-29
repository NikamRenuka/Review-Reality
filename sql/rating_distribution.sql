-- How many reviews gave 1, 2, 3, 4 and 5 stars, for one product family
-- (or for all products when :family is NULL).
-- Concepts: WHERE with an optional filter, GROUP BY, a window function for the share.
SELECT
    r.rating,
    COUNT(*)                                            AS reviews,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
WHERE (:family IS NULL OR p.family = :family)
GROUP BY r.rating
ORDER BY r.rating;
