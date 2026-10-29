-- Do reviews from different shops rate the same product differently?
-- Concepts: GROUP BY two columns, HAVING to hide tiny groups.
SELECT
    p.family,
    r.source_site,
    COUNT(*)                 AS reviews,
    ROUND(AVG(r.rating), 2)  AS avg_rating
FROM reviews AS r
JOIN products AS p ON p.product_id = r.product_id
WHERE (:family IS NULL OR p.family = :family)
GROUP BY p.family, r.source_site
HAVING COUNT(*) >= :min_reviews
ORDER BY p.family, reviews DESC;
