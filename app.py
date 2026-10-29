"""Review Reality dashboard.  Run with:  streamlit run app.py"""
import streamlit as st

from dashboard import data, method, overview, patterns, seller, shopper
from dashboard.style import apply_css

st.set_page_config(page_title="Review Reality", page_icon=":material/reviews:", layout="wide")
apply_css()

brand, note = st.columns([3, 2], vertical_alignment="bottom")
with brand:
    st.html('<div class="rr-brand">Review Reality</div><div class="rr-tagline">Look beyond the stars.</div>')

if not data.database_ready():
    st.divider()
    st.subheader("The review database has not been built yet", anchor=False)
    st.markdown(
        "1. Download the dataset as described in `docs/DATASET.md` and unzip it into `data/raw/datafiniti/`.\n"
        "2. In this folder, run `python -m review_reality.build` (about 2 minutes).\n"
        "3. Refresh this page."
    )
    st.stop()

with note:
    steps = data.table("build_steps")
    st.html(
        f'<div class="rr-note">{steps["rows"].iloc[-1]:,} unique reviews of Amazon devices, 2009–2019<br>'
        'Data: Datafiniti via Kaggle (CC BY-NC-SA 4.0)</div>'
    )

pages = st.navigation(
    [
        st.Page(overview.render, title="Overview", icon=":material/insights:", default=True),
        st.Page(shopper.render, title="Shopper insights", icon=":material/shopping_bag:", url_path="shopper"),
        st.Page(seller.render, title="Seller insights", icon=":material/storefront:", url_path="seller"),
        st.Page(patterns.render, title="Review patterns", icon=":material/troubleshoot:", url_path="patterns"),
        st.Page(method.render, title="Data & method", icon=":material/menu_book:", url_path="method"),
    ],
    position="top",
)
pages.run()
