-- Near-identical reviews of the same product written under different reviewer names.
-- Returns every review that is part of at least one similar pair, plus each pair's similarity.
-- Concepts: UNION to stack both sides of each pair, joining the same table twice.
WITH members AS (
    SELECT review_id_a AS review_id FROM similar_pairs
    UNION
    SELECT review_id_b FROM similar_pairs
)
SELECT
    p.family,
    r.review_id,
    r.review_date,
    r.rating,
    r.source_site,
    r.text,
    (SELECT MAX(sp.similarity) FROM similar_pairs AS sp
     WHERE sp.review_id_a = r.review_id OR sp.review_id_b = r.review_id) AS max_similarity
FROM members AS m
JOIN reviews AS r ON r.review_id = m.review_id
JOIN products AS p ON p.product_id = r.product_id
WHERE (:family IS NULL OR p.family = :family)
ORDER BY p.family, r.review_date;
