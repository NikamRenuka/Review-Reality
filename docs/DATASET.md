# Dataset

## Source and licence

| | |
|---|---|
| Name | Consumer Reviews of Amazon Products |
| Publisher | Datafiniti (on Kaggle) |
| Link | https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products |
| Licence | **CC BY-NC-SA 4.0** (checked in Kaggle's dataset record on 2026-10-29) |
| What the licence means | Free to use and adapt for **non-commercial** work, with **credit** to Datafiniti, and anything shared must use the same licence. |
| Last updated on Kaggle | 2019-05-20 |

**How this project respects the licence:** the raw files are never uploaded to GitHub (`data/raw/` is in `.gitignore`), the project is non-commercial, and this page credits the source.

## How to download (free Kaggle account, no card needed)

1. Open the link above and sign in.
2. Click **Download → Download dataset as zip** (about 17 MB).
3. Unzip it into `data/raw/datafiniti/`. You should have the three CSV files below.

## Files

| Our key | File | Rows | Review dates |
|---|---|---|---|
| `2018_04` | `1429_1.csv` | 34,660 | 2010-07 to 2018-04 |
| `2018_09` | `Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv` | 5,000 | 2014-10 to 2018-09 |
| `2019_05` | `Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19.csv` | 28,332 | 2009-02 to 2019-03 |

The three files are different snapshots of the same collection and **overlap** (many reviews appear in more than one file). We use all three and remove the copies.

## Columns we use (data dictionary)

| Raw column | Our name | Meaning | Notes |
|---|---|---|---|
| `name` | `listing_name` | Product listing title | Missing for 6,760 rows of the oldest file; filled from other rows with the same ASIN, or from the product slug in `keys` (9 ASINs, see `products.py`). |
| `asins` | `asins` | Amazon product code(s) | Some rows list two codes, separated by a comma. |
| `reviews.date` | `review_date` | Date the review was written | ISO format; all values parse. 39 missing in the oldest file. |
| `reviews.rating` | `rating` | Stars, 1 to 5 | 33 missing in the oldest file. |
| `reviews.title` | `title` | Review headline | |
| `reviews.text` | `text` | Review text | 1 missing. |
| `reviews.username` | `username` | Reviewer's public display name | Replaced by an anonymous ID during cleaning and then dropped. |
| `reviews.doRecommend` | `recommends` | Reviewer says they would recommend it | Missing for about 43% of the newest file. |
| `reviews.numHelpful` | `helpful_votes` | "Helpful" votes from other shoppers | Missing for about 43% of the newest file. |
| `reviews.sourceURLs` | `source_url` | Page the review was collected from | Used to find the shop (Best Buy, Amazon, ...). |

Columns we do **not** use: image URLs, internal IDs, `reviews.didPurchase` (100% missing in the newest file, so there is **no verified-purchase information**), and the reviewer's city and province (personal information we do not need).

## Known issues and limitations

1. **The products are made by Amazon, but most reviews are not from Amazon.com.** In the newest file, 16,043 reviews come from bestbuy.com and 12,144 from amazon.com; in the oldest file, 34,057 of 34,660 come from Best Buy.
2. **Copied reviews.** The same review (same user, same text, same date) is attached to several colour or size listings of one product. In the newest file, 28,332 rows hold only about 19,300 different reviews. We group listings into **product families** and remove copies inside each family.
3. **Strong positive skew.** In the newest file, 19,897 of 28,332 ratings are 5 stars and only 965 are 1 star. Averages hide problems, which is exactly why we look at complaints.
4. **Few products.** About 20 product families, dominated by Fire tablets, batteries, Echo, Fire TV and Kindle.
5. **No fake-review labels.** Nothing in the data says whether a review is genuine. We can show *unusual patterns worth checking*, never proof of fake reviews.
6. **Old data.** Reviews end in March 2019, so findings describe those products at that time, not today's market.
7. **No prices, no seller data, no returns data.** We do not invent them.
