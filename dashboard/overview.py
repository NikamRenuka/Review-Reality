"""Overview: the whole idea on one page. Products with similar stars can have very different complaint levels."""
import plotly.graph_objects as go
import streamlit as st

from dashboard import data
from dashboard.style import ACCENT, GREY, INK_MUTED, heading, insight, pct, show, table_height
from review_reality.insights import similar_stars_biggest_gap

CHART_MIN_REVIEWS = 300
LABEL_MIN_REVIEWS = 3000


def point_labels(table, highlight):
    """Label the highlighted products and the big ones, but skip a label that would sit on top of
    an already-labelled point (for example AA and AAA batteries, which are almost in the same place)."""
    labelled, labels = [], []
    order = sorted(table.index, key=lambda i: (table.at[i, "family"] not in highlight, -table.at[i, "reviews"]))
    chosen = {}
    for i in order:
        family, x, y = table.at[i, "family"], table.at[i, "avg_rating"], table.at[i, "pct_with_complaint"]
        crowded = any(abs(x - lx) < 0.06 and abs(y - ly) < 1.5 for lx, ly in labelled)
        if (family in highlight or table.at[i, "reviews"] >= LABEL_MIN_REVIEWS) and not crowded:
            chosen[i] = family
            labelled.append((x, y))
    for i in table.index:
        labels.append(chosen.get(i, ""))
    return labels


def render():
    heading(
        "Overview",
        "Same stars, different stories",
        "Average star ratings on these products are all between about 4.3 and 4.8, so they look alike. "
        "Reading what reviewers actually wrote shows which products collect repeated complaints, and about what.",
    )

    table = data.products(CHART_MIN_REVIEWS)
    steps = data.table("build_steps")
    ratings = data.rating_distribution()
    five_star = ratings.loc[ratings["rating"] == 5, "pct"].item()
    all_products = data.products(1)
    with_complaint = (all_products["pct_with_complaint"] * all_products["reviews"]).sum() / all_products["reviews"].sum()

    cols = st.columns(4)
    cols[0].metric("Unique reviews analysed", f"{steps['rows'].iloc[-1]:,}", border=True,
                   help="After removing reviews copied across colour/size listings and snapshot files.")
    cols[1].metric(f"Products with {CHART_MIN_REVIEWS}+ reviews", len(table), border=True)
    cols[2].metric("Five-star reviews", pct(five_star), border=True,
                   help="Share of all reviews that gave 5 stars. Averages this high hide problems.")
    cols[3].metric("Reviews with a complaint", pct(with_complaint), border=True,
                   help="Reviews with at least one sentence about a product aspect that the text model scores as clearly negative.")

    st.space("small")
    finding = similar_stars_biggest_gap(table)
    if finding:
        insight(
            f"<b>{finding['more']}</b> and <b>{finding['fewer']}</b> have almost the same average rating "
            f"({finding['more_stars']:.2f}★ and {finding['fewer_stars']:.2f}★), but "
            f"{pct(finding['more_pct'])} of reviews for the first contain a complaint, against {pct(finding['fewer_pct'])} "
            f"for the second."
        )

    st.space("small")
    st.subheader("Star rating vs. complaints", anchor=False)
    st.caption(f"Each circle is a product family with at least {CHART_MIN_REVIEWS} reviews. Circle size = number of reviews. "
               "Higher up = more reviews contain a complaint.")
    highlight = {finding["more"], finding["fewer"]} if finding else set()
    colours = [ACCENT if f in highlight else GREY for f in table["family"]]
    labels = point_labels(table, highlight)
    fig = go.Figure(go.Scatter(
        x=table["avg_rating"], y=table["pct_with_complaint"], mode="markers+text",
        text=labels, textposition=["top center" if f in highlight else "bottom center" for f in table["family"]],
        textfont=dict(size=11, color=INK_MUTED),
        marker=dict(size=table["reviews"], sizemode="area", sizeref=table["reviews"].max() / 2200, sizemin=6,
                    color=colours, line=dict(color="white", width=1)),
        customdata=table[["family", "reviews", "pct_negative", "top_complaint"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{x:.2f}★ average · %{customdata[1]:,} reviews"
                      "<br>%{y:.1f}% of reviews contain a complaint<br>%{customdata[2]:.1f}% gave 1–2★"
                      "<br>Top complaint: %{customdata[3]}<extra></extra>",
    ))
    fig.update_xaxes(title="Average star rating", tickformat=".1f")
    fig.update_yaxes(title="% of reviews with a complaint", ticksuffix="%", rangemode="tozero")
    show(fig, height=430)

    st.subheader("All products", anchor=False)
    st.dataframe(
        table[["family", "category", "reviews", "avg_rating", "pct_negative", "pct_with_complaint", "top_complaint"]],
        hide_index=True, width="stretch", height=table_height(len(table)),
        column_config={
            "family": "Product", "category": "Category",
            "reviews": st.column_config.NumberColumn("Reviews", format="localized"),
            "avg_rating": st.column_config.NumberColumn("Avg ★", format="%.2f"),
            "pct_negative": st.column_config.NumberColumn("1–2★ reviews", format="%.1f%%"),
            "pct_with_complaint": st.column_config.ProgressColumn(
                "Reviews with a complaint", format="%.1f%%", min_value=0, max_value=float(table["pct_with_complaint"].max()),
                color=ACCENT),
            "top_complaint": "Most common complaint",
        },
    )
    st.caption("Complaint figures are estimates from keyword rules and a text model (about 3 in 4 flagged sentences are real "
               "complaints in a hand check). Use them to compare products, and read the example sentences on the other pages. "
               "See Data & method.")
