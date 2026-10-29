# Review Reality

**Look Beyond the Stars.**

Review Reality is a review analytics project. It helps:

- **Shoppers** look past the average star rating: how ratings are spread, what people praise, and which complaints keep coming back.
- **Sellers** find the most common complaints, see which product parts get good or bad feedback, and see how feedback changes over time.

Example question: a product has 4.8 stars, but many reviews mention battery problems. Another has 4.5 stars and fewer repeated complaints. Which one is the safer buy? Review Reality answers questions like this with evidence from real review data.

> **Status:** Phase 2 done (dataset chosen and documented). No findings yet. Nothing in this project is a finding until it is calculated from the real dataset.

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
│   └── DATASET.md       Source, licence, data dictionary, known issues
├── review_reality/      Reusable Python code
│   ├── paths.py         All file locations
│   ├── load.py          Read the raw CSVs, rename columns
│   └── products.py      Group listings into product families
├── sql/                 SQL query files (Phase 3)
├── app.py               Streamlit dashboard (Phase 6)
└── tests/               pytest tests
```

## Setup (Windows)

```powershell
cd "$HOME\Desktop\Review-Reality"
py -m venv .venv                 # make the virtual environment (only once)
.venv\Scripts\Activate.ps1       # turn it on (each new terminal)
python --version                 # should show Python 3.15.x
python -m pip install -r requirements.txt   # install the libraries (only once)
```

If PowerShell blocks `Activate.ps1`, run this once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Progress

- [x] **Phase 1:** Environment and project setup
- [x] **Phase 2:** Choose and understand the dataset
- [ ] **Phase 3:** Data cleaning and SQL
- [ ] **Phase 4:** Exploratory data analysis
- [ ] **Phase 5:** Core analytics (sentiment, complaint types, similar reviews, comparisons)
- [ ] **Phase 6:** Dashboard (Shopper and Seller views)
- [ ] **Phase 7:** Testing and quality checks
- [ ] **Phase 8:** Documentation and interview preparation

## Data source and licence

[Consumer Reviews of Amazon Products](https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products) by **Datafiniti**, licensed **CC BY-NC-SA 4.0**. Reviews of Amazon-made devices (Fire tablets, Kindle, Echo, Fire TV, AmazonBasics batteries), collected mostly from Best Buy and Amazon, 2009–2019.
The raw data is not included in this repository. See [docs/DATASET.md](docs/DATASET.md) for download steps, the data dictionary and known limitations.
