-- Near-identical reviews of the same product written under different reviewer names.
-- Concepts: joining the same table twice with different aliases (a and b).
SELECT
    p.family,
    sp.similarity,
    a.review_date  AS date_a,
    b.review_date  AS date_b,
    a.rating       AS rating_a,
    b.rating       AS rating_b,
    a.source_site  AS site_a,
    b.source_site  AS site_b,
    a.text         AS text_a,
    b.text         AS text_b
FROM similar_pairs AS sp
JOIN reviews AS a ON a.review_id = sp.review_id_a
JOIN reviews AS b ON b.review_id = sp.review_id_b
JOIN products AS p ON p.product_id = a.product_id
WHERE (:family IS NULL OR p.family = :family)
ORDER BY sp.similarity DESC, p.family;
