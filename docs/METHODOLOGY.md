# Methodology

How Review Reality turns raw reviews into the numbers on the dashboard, and how far each number can be trusted.
Exact results are in [ANALYSIS_RESULTS.md](ANALYSIS_RESULTS.md) (regenerated on every build).

## 1. Cleaning (review_reality/clean.py)

| Step | Why |
|---|---|
| Stack the three snapshot files | They cover different time ranges and products. |
| Fill missing product names from the ASIN | 6,760 rows in the oldest file had no name. |
| Group listings into **product families** | Colour/size variants are the same product to a shopper. |
| Convert ratings, dates, votes; invalid values become missing | One bad value should not crash the pipeline or count as a real value. |
| Drop rows with no rating or no text | They cannot be analysed (34 rows). |
| **Remove copies**: one row per (family, reviewer name, text) | The same review was attached to every colour of a product and repeated across snapshot files (16,795 rows removed). Counting copies would inflate popular products. |
| Replace usernames with an anonymous `reviewer_id` (SHA-256, first 12 characters) | We can still group by reviewer without storing names. |

## 2. Product aspects: keyword rules (review_reality/aspects.py)

1. Split each review into sentences.
2. Tag a sentence with an aspect (Battery life, Leaking, Speed & performance, ...) if it contains one of that aspect's words or phrases.
3. Drop aspects that describe a *different* device. Example: "the batteries in my remote died" is about battery life, not about a remote.

**Where the word lists came from:** for each product category we counted which words and two-word phrases appear much more often in 1-2 star reviews than in 4-5 star reviews (a log-ratio with smoothing). Examples: batteries → "leaked", "acid", "bad batch", "short life"; tablets → "slow", "freezes", "charging". We grouped these into readable aspects and added common synonyms.

**Why rules and not a model:** they are transparent (anyone can read the word list), fast, and need no labelled training data, which we do not have.

**Known weaknesses:** they miss unusual wording, and can match the wrong meaning ("I bought it at **last**").

## 3. Text sentiment: TF-IDF + logistic regression (review_reality/sentiment.py)

**Why we need it:** stars describe a whole review. A 5-star review can still contain a complaint ("love it, but the battery drains fast"). To find complaints *inside* reviews, we need to score individual sentences.

**Training labels:** 1-2 stars = negative, 4-5 stars = positive, 3 stars left out (mixed). No manual labelling.

**Test (20% of reviews never seen in training; identical texts kept on one side of the split):**

| Measure | Model | Baseline (always "positive") |
|---|---|---|
| Balanced accuracy | 0.895 | 0.500 |
| Recall on negative reviews | 0.822 | 0.000 |
| Precision on negative reviews | 0.540 | (none) |

Reading this: the model finds about 4 of every 5 negative reviews, but about half of what it calls negative is actually positive. That is fine for pointing at sentences worth reading; it is not good enough to be quoted as an exact count.

**Complaint threshold:** a sentence is a *complaint* when its negative probability is at least **0.7**. At 0.5, reading samples showed too much praise being flagged ("I was worried it would lag, but it didn't").

**Hand check:** we read 50 randomly chosen sentences with probability ≥ 0.7 that mention an aspect. **38 of 50 (76%) were real complaints about the tagged aspect.** The misses were mostly conditional praise ("If you don't need X, it's great"), neutral facts, or the wrong aspect. So complaint counts are **estimates**, and the dashboard always shows the example sentences behind them.

**Review-level scores** (used for star/text mismatches) are **out-of-fold**: each review is scored by a model trained on the other 80% of reviews, so a review is never scored by a model that memorised it.

## 4. Unusual patterns (worth checking, never "fake")

| Pattern | Method | What it can and cannot tell us |
|---|---|---|
| Near-identical reviews | TF-IDF cosine similarity ≥ 0.8 between reviews of the same family by different reviewer names (texts of 60+ characters) | Same text under two names could be one person with two accounts, a review syndicated between shops, or a data-collection error. |
| Review bursts | Days with 20+ reviews and at least 5× the product's average reviews per day (SQL window function) | Most bursts fall between Dec 23 and Jan 23 (gift season) and have the same average rating as normal days. A burst with a *higher* rating than usual deserves more attention. |
| Star/text mismatch | 4-5 stars with text ≥ 0.9 negative, or 1-2 stars with text ≤ 0.1 | Often mis-clicks or mixed reviews. Useful for sellers to read. |

**What we deliberately do not analyse:** reviewer-level activity. Reviewer names are public display names, and many people share the same one ("Byamazon customer" appears 861 times, "mIKE" 182 times). Counting reviews per name would wrongly suggest that one person wrote hundreds of reviews.

## 5. Limitations

- No ground truth for fake reviews; no verified-purchase flag.
- Data ends in March 2019 and mostly comes from Best Buy.
- Strong positive skew (70% five-star), so negative-review samples are small for some products (for example, about 70 for all e-readers together).
- Complaint numbers depend on the keyword lists and the 0.7 threshold. They are best used to **compare** aspects and products measured the same way, not as exact counts.
