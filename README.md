# Review Reality

**Look Beyond the Stars.**

Review Reality is a review analytics project. It helps:

- **Shoppers** look past the average star rating: how ratings are spread, what people praise, and which complaints keep coming back.
- **Sellers** find the most common complaints, see which product parts get good or bad feedback, and see how feedback changes over time.

Example question: a product has 4.8 stars, but many reviews mention battery problems. Another has 4.5 stars and fewer repeated complaints. Which one is the safer buy? Review Reality answers questions like this with evidence from real review data.

> **Status:** Phase 6 done (dashboard built and tested). Final testing and documentation come next. Nothing in this project is a finding until it is calculated from the real dataset.

## Honest limits (we will keep these all through the project)

- An unusual review is **not** proof of a fake review. We report "patterns worth checking", never "fake".
- We use only a free, public dataset with a clear licence. No scraping, no paid APIs, no live marketplace data.
- Every number in the dashboard comes from code that runs on the dataset. No made-up statistics.

## Tech stack (all free, all run on this laptop)

| Tool | Why |
|---|---|
| Python 3.15 | Main language |
| pandas, NumPy | Load, clean and summarise data |
| SQLite + SQL | Store clean data and answer questions with SQL queries |
| Streamlit | The dashboard (web app that runs locally) |
| Plotly | Interactive charts |
| scikit-learn | Only if a simple method is not good enough |
| pytest | Automatic tests |
| Git + GitHub | Version control and portfolio |

Exact versions are in `requirements.txt` (all tested on Python 3.15.1).

## Planned folder structure

Folders are created in the phase that first needs them.

```
Review-Reality/
├── README.md            Project overview, setup steps, progress
├── .gitignore           Files Git must never save (venv, data, secrets)
├── requirements.txt     Exact library list
├── pyproject.toml       Project settings (tells pytest where the code is)
├── data/                NOT in Git
│   ├── raw/datafiniti/  The three Kaggle CSV files
│   └── processed/       Cleaned SQLite database (Phase 3)
├── docs/
│   ├── DATASET.md           Source, licence, data dictionary, known issues
│   ├── METHODOLOGY.md       How each number is calculated and how far to trust it
│   ├── DATA_QUALITY.md      Generated: cleaning counts, missing values
│   └── ANALYSIS_RESULTS.md  Generated: model scores, complaints per product, patterns
├── review_reality/      Reusable Python code
│   ├── paths.py         All file locations
│   ├── load.py          Read the raw CSVs, rename columns
│   ├── products.py      Group listings into product families
│   ├── clean.py         Fix types, remove unusable rows and copied reviews, anonymise reviewers
│   ├── db.py            Save to SQLite, run SQL files
│   ├── aspects.py       Keyword rules: which aspect a sentence talks about
│   ├── sentiment.py     Text model: how negative a sentence sounds (tested on held-out reviews)
│   ├── analytics.py     Aspect complaints, out-of-fold review scores, similar reviews
│   └── build.py         Run everything: python -m review_reality.build
├── sql/                 One SQL file per question (summary, ratings, trends, bursts, aspects, mismatches)
├── app.py               Streamlit dashboard entry point (streamlit run app.py)
├── dashboard/           One file per dashboard page, plus data.py (cached SQL) and style.py (look and feel)
├── .streamlit/          Theme (colours, fonts) and settings (usage statistics off)
└── tests/               pytest tests, including headless runs of every dashboard page
```

## Setup (Windows)

```powershell
cd "$HOME\Desktop\Review-Reality"
py -m venv .venv                 # make the virtual environment (only once)
.venv\Scripts\Activate.ps1       # turn it on (each new terminal)
python --version                 # should show Python 3.15.x
python -m pip install -r requirements.txt   # install the libraries (only once)
python -m review_reality.build   # clean, analyse, build data/processed/reviews.db (about 2 min)
python -m pytest                 # run the tests
streamlit run app.py             # open the dashboard at http://localhost:8501
```

## Dashboard

| Page | What it answers |
|---|---|
| **Overview** | Which products have similar stars but very different complaint levels? |
| **Shopper insights** | For one product (or two side by side): how ratings are spread, the most common complaints, and complaints hidden inside 4–5★ reviews. |
| **Seller insights** | Complaint priorities, whether each complaint is rising or falling by quarter, customers' own words, ratings by shop, and reviews whose stars and words disagree. |
| **Review patterns** | Review bursts (compared with the product's usual rating) and groups of near-identical reviews under different names, clearly labelled as patterns, not proof. |
| **Data & method** | Source, licence, cleaning funnel, model test scores, hand-check result and limitations. |

Every number on every page is calculated by a SQL file in `sql/` on the database built by `review_reality.build`.

If PowerShell blocks `Activate.ps1`, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Progress

- [x] **Phase 1:** Environment and project setup
- [x] **Phase 2:** Choose and understand the dataset
- [x] **Phase 3:** Data cleaning and SQL (67,992 raw rows → 51,163 unique reviews; see [docs/DATA_QUALITY.md](docs/DATA_QUALITY.md))
- [x] **Phase 4:** Exploratory data analysis (complaint words found from the data itself)
- [x] **Phase 5:** Core analytics (sentence-level aspect complaints, text model with balanced accuracy 0.895 on held-out reviews, similar reviews, bursts, star/text mismatches; see [docs/METHODOLOGY.md](docs/METHODOLOGY.md))
- [x] **Phase 6:** Dashboard (Overview, Shopper, Seller, Review patterns, Data & method)
- [ ] **Phase 7:** Testing and quality checks
- [ ] **Phase 8:** Documentation and interview preparation

## Data source and licence

[Consumer Reviews of Amazon Products](https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products) by **Datafiniti**, licensed **CC BY-NC-SA 4.0**. Reviews of Amazon-made devices (Fire tablets, Kindle, Echo, Fire TV, AmazonBasics batteries), collected mostly from Best Buy and Amazon, 2009–2019.
The raw data is not included in this repository. See [docs/DATASET.md](docs/DATASET.md) for download steps, the data dictionary and known limitations.
