"""Review patterns: unusual activity worth a closer look. Patterns, never proof of fake reviews."""
import plotly.graph_objects as go
import streamlit as st

from dashboard import data
from dashboard.style import ACCENT, GREY_DARK, heading, pct, quote, show, stars
from review_reality.insights import group_similar

ALL = "All products"


def render():
    heading(
        "Review patterns",
        "Worth a closer look",
        "Unusual activity in the reviews: sudden bursts of reviews and near-identical texts under different names. "
        "<b>These are patterns, not proof.</b> The dataset has no labels saying which reviews are genuine, "
        "and each pattern has innocent explanations.",
    )
    family = st.selectbox("Product", [ALL] + data.product_names(), key="patterns_product")
    selected = None if family == ALL else family

    bursts = data.bursts(selected)
    similar = data.similar(selected)
    cols = st.columns(3)
    cols[0].metric("Review bursts", len(bursts), border=True,
                   help="Days with 20+ reviews and at least 5 times the product's average reviews per day.")
    cols[1].metric("Reviews in near-identical groups", len(similar), border=True,
                   help="Reviews of the same product, under different reviewer names, with at least 80% similar wording "
                        "to another review.")
    cols[2].metric("Bursts in Dec–Jan", pct(100 * bursts["day"].str[5:7].isin(["12", "01"]).mean()) if len(bursts) else "–",
                   border=True, help="Holiday gifts are a common innocent reason for a burst of reviews.")

    st.subheader("Review bursts", anchor=False)
    if bursts.empty:
        st.info("No review bursts for this selection.", icon=":material/info:")
    else:
        normal = data.products(1).set_index("family")["avg_rating"]
        bursts = bursts.assign(product_avg=bursts["family"].map(normal))
        bursts["rating_vs_usual"] = (bursts["avg_rating"] - bursts["product_avg"]).round(2)
        st.caption("Compare each burst's average rating with the product's usual average. A burst that is much more "
                   "positive than usual deserves more attention than one that matches it.")
        st.dataframe(
            bursts[["family", "day", "reviews", "times_typical", "avg_rating", "product_avg", "rating_vs_usual"]],
            hide_index=True, width="stretch", height=300,
            column_config={
                "family": "Product", "day": "Day",
                "reviews": st.column_config.NumberColumn("Reviews that day", format="localized"),
                "times_typical": st.column_config.NumberColumn("× usual day", format="%.1f×"),
                "avg_rating": st.column_config.NumberColumn("Avg ★ that day", format="%.2f"),
                "product_avg": st.column_config.NumberColumn("Usual avg ★", format="%.2f"),
                "rating_vs_usual": st.column_config.NumberColumn("Difference", format="%+.2f"),
            },
        )
        if selected:
            timeline(selected, bursts)

    st.subheader("Near-identical reviews", anchor=False)
    if similar.empty:
        st.info("No near-identical reviews by different names for this selection.", icon=":material/info:")
        return
    st.caption("Reviews linked by at least 80% similar wording are grouped together. Possible explanations: one person "
               "with several accounts, a review shared between shops, or a data-collection error. Reviewer names are not shown.")
    by_id = similar.set_index("review_id")
    for group in group_similar(data.similar_pairs()):
        if not group <= set(by_id.index):
            continue  # group belongs to another product
        rows = by_id.loc[sorted(group)].sort_values("review_date")
        first, last = rows["review_date"].min(), rows["review_date"].max()
        label = (f"{rows['family'].iloc[0]} · {len(rows)} reviews under different names · "
                 f"{first} to {last} · up to {rows['max_similarity'].max():.0%} similar")
        with st.expander(label):
            for row in rows.itertuples():
                quote(row.text, f"{stars(row.rating)} · {row.review_date} · {row.source_site}")


def timeline(family, bursts):
    daily = data.daily(family)
    burst_days = set(bursts["day"])
    st.caption(f"Reviews per day for {family}. Burst days are highlighted.")
    fig = go.Figure()
    fig.add_bar(x=daily["day"], y=daily["reviews"], marker_color=[ACCENT if d in burst_days else GREY_DARK for d in daily["day"]],
                customdata=daily["avg_rating"], hovertemplate="%{x}: %{y} reviews, avg %{customdata:.2f}★<extra></extra>")
    fig.update_layout(bargap=0)
    fig.update_yaxes(title="Reviews per day")
    show(fig, height=260)
