# Interview preparation: Review Reality

## 60-second introduction

> "Review Reality is a review analytics dashboard. Star ratings hide a lot: most products I looked at have between 4.3 and 4.8 stars, so they all look good. I wanted to show what the reviews actually say.
>
> I used a public Kaggle dataset of about 68,000 reviews of Amazon devices, like Fire tablets, Kindles and AmazonBasics batteries. First I cleaned it. I found that the same review was copied onto every colour of a product, so 25% of the rows were copies. After removing them I had 51,000 unique reviews, which I stored in SQLite and analysed with SQL.
>
> Then I split reviews into sentences, tagged each sentence with an aspect like battery life or screen, and used a simple text model to find complaint sentences, even inside 5-star reviews. I tested the model on reviews it had never seen and checked 50 results by hand.
>
> The main finding: AAA batteries and the Kindle e-reader have almost the same rating, but battery reviews contain complaints much more often, mostly about short battery life and leaking. I built a Streamlit dashboard with a shopper view, a seller view, and a page for unusual review patterns. I was careful to call those patterns, not proof of fake reviews."

## Likely questions and answers

**1. Why did you choose this dataset?**
It has real product names, review text, ratings and dates, and it is electronics, where repeated weaknesses like battery problems are common. It is small enough to work with on a laptop. Most importantly, it has a clear licence (CC BY-NC-SA 4.0). I rejected a bigger Amazon dataset because I could not find its licence.

**2. What was the hardest data-cleaning problem?**
Copied reviews. The same review, by the same person on the same date, was attached to every colour and size of a product, and also repeated across three snapshot files. If I had counted rows, popular products would look much bigger. I grouped listings into product families with rules (for example, all Fire HD 8 colours become "Fire HD 8 Tablet") and removed copies inside each family: 67,992 rows became 51,163.

**3. Why SQLite and not just pandas?**
SQL is the main skill for analyst jobs, and a database makes the dashboard fast and simple: every chart is one SQL file. I used pandas for cleaning, then I wrote a test that recalculates the SQL results with pandas to make sure both agree.

**4. Explain one SQL query you wrote.**
`review_bursts.sql`: first a CTE counts reviews per product per day. Then a window function, `AVG(reviews) OVER (PARTITION BY product_id)`, gives each product's typical daily count. Finally I keep days with at least 20 reviews and at least 5 times the typical count.

**5. How do you find complaints?**
Three steps. Split each review into sentences. Tag sentences with aspects using keyword rules (the keywords came from words much more common in 1–2 star reviews). Score each sentence with a text model; if it is at least 70% likely to be negative, it counts as a complaint.

**6. What is TF-IDF? What is logistic regression?**
TF-IDF turns text into numbers. A word gets a high weight when it appears in this text but is rare in other texts, so common words like "the" matter little. Logistic regression is a simple model that learns a weight for each word and turns the total into a probability between 0 and 1, here "how likely is this negative".

**7. How did you label data for the model?**
I did not label by hand. I used the star ratings: 1–2 stars = negative, 4–5 stars = positive, and I left out 3 stars because they are mixed.

**8. How good is the model?**
On 20% of reviews it never saw, balanced accuracy is 0.895 against 0.5 for always guessing "positive". Recall is 0.82 (it finds most negative reviews) but precision is 0.54 (about half of what it flags is not negative). That is why I set a stricter 70% threshold for sentences, and I read 50 random flagged sentences by hand: 38 were real complaints.

**9. Why balanced accuracy and not normal accuracy?**
Only about 4% of reviews are negative. A model that always says "positive" would get 96% normal accuracy and be useless. Balanced accuracy averages the score on each class, so that model gets 0.5.

**10. Can your project detect fake reviews?**
No, and I say so in the dashboard. The data has no labels saying which reviews are fake. I show patterns worth checking: review bursts and near-identical texts under different names. Each has innocent explanations. For example, two-thirds of bursts are in December and January, which fits holiday gifts, and every burst day's average rating is within 0.28 stars of the product's usual average.

**11. Why did you not analyse reviewers?**
Reviewer names are display names, not people. "Byamazon customer" appears 861 times and "mIKE" 182 times. Counting reviews per name would wrongly suggest that one person wrote hundreds of reviews.

**12. What would you improve?**
Hand-label a few hundred aspect sentences to measure and improve the keyword rules, handle negation like "it didn't lag", and add newer data.

**13. How did you test the project?**
68 automated tests with pytest: cleaning rules, every SQL file against answers I worked out by hand, the analytics, a check that SQL equals pandas on the real data, and headless runs of every dashboard page for every product.

**14. What is one bug you found and fixed?**
I used `with sqlite3.connect(...) as conn`, thinking it closes the connection. It does not; it only commits. Tests showed 199 "unclosed database" warnings. I wrote a small helper that always closes the connection, and the warnings went to zero.

## Resume bullet points (all verified)

- Built **Review Reality**, a Streamlit dashboard that analyses 51,163 product reviews to reveal recurring complaints hidden behind average star ratings (Python, pandas, SQLite, scikit-learn, Plotly).
- Cleaned 67,992 raw review rows from three overlapping files, removing 25% duplicate reviews by grouping 111 product listings into 20 product families.
- Wrote 12 SQL queries using joins, CTEs and window functions for product summaries, monthly trends, complaint rates and review-burst detection.
- Detected sentence-level complaints with keyword rules and a TF-IDF + logistic regression model (balanced accuracy 0.895 on held-out reviews; 76% precision in a 50-sentence hand check).
- Wrote 68 pytest tests, including a cross-check of SQL results against pandas and automated runs of every dashboard page; managed the project with Git and GitHub.

## Demo plan (3 minutes)

1. **Overview:** point at the highlighted pair: similar stars, different complaint rates.
2. **Shopper insights:** pick *AmazonBasics AAA Batteries*, show "What people complain about", then click *Leaking* under hidden complaints.
3. **Seller insights:** pick *Fire 7 Tablet*, show complaint priorities and the trend chart.
4. **Review patterns:** open the 5-review group, and say "pattern, not proof".
5. **Data & method:** show the cleaning funnel and the model test scores.

## Be honest about how you built it

If you are asked whether you used AI tools, say yes, and explain what you checked yourself: the licence, the cleaning counts, the hand check of 50 sentences, and the test results. Before an interview, run the project once, read `clean.py` and `review_bursts.sql`, and make sure you can explain every bullet above in your own words.
