-- Real example sentences behind a complaint number, most negative first.
-- :max_rating lets us show only "hidden" complaints inside 4-5 star reviews.
SELECT
    m.sentence,
    m.neg_prob,
    r.rating,
    r.review_date,
    r.source_site,
    r.helpful_votes
FROM aspect_mentions AS m
JOIN reviews AS r ON r.review_id = m.review_id
JOIN products AS p ON p.product_id = r.product_id
WHERE p.family = :family
  AND m.aspect = :aspect
  AND m.neg_prob >= :threshold
  AND r.rating BETWEEN :min_rating AND :max_rating
ORDER BY m.neg_prob DESC, r.helpful_votes DESC
LIMIT :limit;
