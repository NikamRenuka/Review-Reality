"""Seller insights: which problems to fix first, whether they are getting better, and what customers said."""
import plotly.graph_objects as go
import streamlit as st

from dashboard import data
from dashboard.style import ACCENT, GREY, heading, pct, quote, show, stars, table_height

RATING_FILTERS = {"All ratings": (1, 5), "1–2★": (1, 2), "3★": (3, 3), "4–5★": (4, 5)}
MIN_QUARTER_REVIEWS = 100


def render():
    heading(
        "Seller insights",
        "What to fix first",
        "Complaint priorities for one product, how each complaint changed over time, and the customers' own words.",
    )
    family = st.selectbox("Product", data.product_names(), key="seller_product")
    aspects = data.aspects(family)
    complained = aspects[aspects["reviews_complaining"] > 0]

    st.subheader("Complaint priorities", anchor=False)
    st.caption("Sorted by how many reviews complain about each aspect. "
               "'Negative share' = of all sentences that mention the aspect, how many are complaints: a high value means "
               "people rarely praise it.")
    if complained.empty:
        st.info("No complaint sentences were found for this product.", icon=":material/info:")
        return
    st.dataframe(
        complained, hide_index=True, width="stretch", height=table_height(len(complained)),
        column_config={
            "aspect": "Aspect",
            "reviews_mentioning": st.column_config.NumberColumn("Reviews mentioning", format="localized"),
            "reviews_complaining": st.column_config.NumberColumn("Reviews complaining", format="localized"),
            "pct_reviews_complaining": st.column_config.ProgressColumn(
                "% of all reviews", format="%.2f%%", min_value=0,
                max_value=float(complained["pct_reviews_complaining"].max()), color=ACCENT),
            "pct_mentions_negative": st.column_config.NumberColumn("Negative share", format="%.1f%%"),
        },
    )

    st.subheader("Is it getting better or worse?", anchor=False)
    aspect = st.selectbox("Aspect", complained["aspect"].tolist(), key=f"trend_{family}")
    trend = data.aspect_trend(family, aspect, min_reviews=MIN_QUARTER_REVIEWS)
    if len(trend) < 2:
        st.info(f"Not enough reviews per quarter to show a trend (at least {MIN_QUARTER_REVIEWS} reviews in two or more "
                "quarters are needed).", icon=":material/info:")
    else:
        st.caption(f"Share of each quarter's reviews that complain about {aspect.lower()}. "
                   f"Grey bars show how many reviews the quarter had. Quarters with fewer than {MIN_QUARTER_REVIEWS} "
                   "reviews are hidden, because a few reviews can swing the percentage a lot.")
        fig = go.Figure()
        fig.add_bar(x=trend["quarter"], y=trend["reviews"], name="Reviews in quarter", marker_color=GREY, opacity=0.45,
                    yaxis="y2", hovertemplate="%{x}: %{y:,} reviews<extra></extra>")
        fig.add_scatter(x=trend["quarter"], y=trend["pct_reviews_complaining"], name="% complaining", mode="lines+markers",
                        line=dict(color=ACCENT, width=2.5), marker=dict(size=7),
                        customdata=trend["reviews_complaining"],
                        hovertemplate="%{x}: %{y:.2f}% (%{customdata} reviews)<extra></extra>")
        fig.update_layout(yaxis=dict(ticksuffix="%", rangemode="tozero", title="% of reviews complaining"),
                          yaxis2=dict(overlaying="y", side="right", showgrid=False, rangemode="tozero", showticklabels=False))
        show(fig, height=320)

    st.subheader("In customers' words", anchor=False)
    choice = st.segmented_control("Ratings", list(RATING_FILTERS), default="All ratings", key=f"words_{family}_{aspect}")
    low, high = RATING_FILTERS[choice or "All ratings"]
    found = data.examples(family, aspect, min_rating=low, max_rating=high, limit=8)
    if found.empty:
        st.info("No complaint sentences match this filter.", icon=":material/info:")
    for row in found.itertuples():
        helpful = f" · {int(row.helpful_votes)} found helpful" if row.helpful_votes == row.helpful_votes and row.helpful_votes else ""
        quote(row.sentence, f"{stars(row.rating)} · {row.review_date} · {row.source_site}{helpful}")

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Ratings by shop", anchor=False)
        st.caption("Only shops with 20+ reviews of this product.")
        shops = data.sources(family)
        if shops.empty:
            st.info("No shop has 20 or more reviews of this product.", icon=":material/info:")
        else:
            st.dataframe(shops[["source_site", "reviews", "avg_rating"]], hide_index=True, width="stretch",
                         column_config={"source_site": "Shop", "reviews": st.column_config.NumberColumn("Reviews", format="localized"),
                                        "avg_rating": st.column_config.NumberColumn("Avg ★", format="%.2f")})
    with right:
        st.subheader("Stars and words disagree", anchor=False)
        found = data.mismatches(family)
        st.caption(f"{len(found)} reviews where the stars and the text point in opposite directions. Often a mis-click or a "
                   "mixed review, so worth reading.")
        if not found.empty:
            with st.expander("Read them"):
                for row in found.head(15).itertuples():
                    quote(row.text[:400] + ("…" if len(row.text) > 400 else ""),
                          f"{stars(row.rating)} · {row.mismatch} · {row.review_date} · {row.source_site}")
    st.caption(f"Complaint = a sentence about the aspect that the text model scores at least "
               f"{int(data.COMPLAINT_THRESHOLD * 100)}% likely to be negative. See Data & method.")
