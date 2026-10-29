-- For one product family: how often each aspect is mentioned, and how often it is complained about.
-- complaint = a sentence about the aspect that the text model scores >= :threshold negative.
-- Concepts: CTEs, COUNT(DISTINCT ...), CASE inside an aggregate, a scalar subquery for the total.
WITH family_reviews AS (
    SELECT r.review_id
    FROM reviews AS r
    JOIN products AS p ON p.product_id = r.product_id
    WHERE p.family = :family
),
mentions AS (
    SELECT m.*
    FROM aspect_mentions AS m
    JOIN family_reviews AS f ON f.review_id = m.review_id
)
SELECT
    aspect,
    COUNT(DISTINCT review_id)                                                    AS reviews_mentioning,
    COUNT(DISTINCT CASE WHEN neg_prob >= :threshold THEN review_id END)          AS reviews_complaining,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN neg_prob >= :threshold THEN review_id END)
          / (SELECT COUNT(*) FROM family_reviews), 2)                            AS pct_reviews_complaining,
    ROUND(100.0 * SUM(CASE WHEN neg_prob >= :threshold THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_mentions_negative
FROM mentions
GROUP BY aspect
ORDER BY reviews_complaining DESC, reviews_mentioning DESC;
