-- Reviews whose stars and words disagree: 4-5 stars but very negative text,
-- or 1-2 stars but very positive text. Often a mis-click or a mixed review,
-- so these are worth reading, not proof of anything.
SELECT
    p.family,
    r.rating,
    s.text_neg_prob,
    CASE WHEN r.rating >= 4 THEN 'High stars, negative text' ELSE 'Low stars, positive text' END AS mismatch,
    r.review_date,
    r.source_site,
    r.title,
    r.text
FROM reviews AS r
JOIN review_scores AS s ON s.review_id = r.review_id
JOIN products AS p ON p.product_id = r.product_id
WHERE (:family IS NULL OR p.family = :family)
  AND ((r.rating >= 4 AND s.text_neg_prob >= :high) OR (r.rating <= 2 AND s.text_neg_prob <= :low))
ORDER BY ABS(s.text_neg_prob - 0.5) DESC;
