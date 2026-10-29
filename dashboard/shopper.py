"""Shopper insights: what reviewers really say about one product, or how two products compare."""
import plotly.graph_objects as go
import streamlit as st

from dashboard import data
from dashboard.style import ACCENT, GREY, GREY_DARK, heading, insight, pct, quote, show, stars
from review_reality.insights import biggest_aspect_difference

TOP_ASPECTS = 6


def render():
    heading(
        "Shopper insights",
        "Before you buy",
        "Pick a product to see how its ratings are spread, which complaints come up again and again, "
        "and the problems people mention even when they give 4 or 5 stars.",
    )

    names = data.product_names()
    left, right = st.columns(2)
    product = left.selectbox("Product", names, index=0, key="shopper_product")
    compare = right.selectbox("Compare with (optional)", ["None"] + [n for n in names if n != product], key="shopper_compare")

    if compare == "None":
        single_product(product)
    else:
        comparison(product, compare)


def headline_metrics(family, container):
    row = data.summary(family)
    cols = container.columns(4)
    cols[0].metric("Average rating", f"{row['avg_rating']:.2f}★", border=True)
    cols[1].metric("Reviews", f"{row['reviews']:,}", border=True)
    cols[2].metric("Unhappy (1–2★)", pct(row["pct_negative"]), border=True)
    cols[3].metric("Would recommend", pct(row["pct_recommend"]) if row["pct_recommend"] == row["pct_recommend"] else "Not asked",
                   border=True, help="Share of reviewers who answered 'yes' to recommending it. Battery reviews did not include this question.")


def rating_chart(family):
    dist = data.rating_distribution(family).sort_values("rating")  # plotly draws the first bar at the bottom
    fig = go.Figure(go.Bar(
        x=dist["pct"], y=[stars(r) for r in dist["rating"]], orientation="h",
        marker_color=[ACCENT if r <= 2 else GREY for r in dist["rating"]],
        text=[pct(p) for p in dist["pct"]], textposition="outside", cliponaxis=False,
        customdata=dist["reviews"], hovertemplate="%{y}: %{customdata:,} reviews (%{x:.1f}%)<extra></extra>",
    ))
    fig.update_xaxes(visible=False, range=[0, dist["pct"].max() * 1.2])  # room for the labels
    fig.update_yaxes(showgrid=False)
    show(fig, height=230)


def complaint_chart(aspects):
    top = aspects.head(TOP_ASPECTS).iloc[::-1]
    fig = go.Figure(go.Bar(
        x=top["pct_reviews_complaining"], y=top["aspect"], orientation="h", marker_color=ACCENT,
        text=[pct(p) for p in top["pct_reviews_complaining"]], textposition="outside", cliponaxis=False,
        customdata=top[["reviews_complaining", "reviews_mentioning", "pct_mentions_negative"]],
        hovertemplate="<b>%{y}</b><br>%{customdata[0]:,} reviews complain about it (%{x:.2f}% of all reviews)"
                      "<br>Mentioned in %{customdata[1]:,} reviews; %{customdata[2]:.1f}% of mentions are negative<extra></extra>",
    ))
    fig.update_xaxes(visible=False, range=[0, top["pct_reviews_complaining"].max() * 1.15])
    fig.update_yaxes(showgrid=False)
    show(fig, height=40 + 38 * len(top))


def single_product(family):
    headline_metrics(family, st)
    aspects = data.aspects(family)

    left, right = st.columns([2, 3], gap="large")
    with left:
        st.subheader("How people rated it", anchor=False)
        st.caption("Share of reviews by stars. 1–2★ highlighted.")
        rating_chart(family)
    with right:
        st.subheader("What people complain about", anchor=False)
        st.caption("Share of all reviews with at least one complaint sentence about each aspect.")
        if aspects.empty or aspects["reviews_complaining"].sum() == 0:
            st.info("No complaint sentences were found for this product.", icon=":material/info:")
        else:
            complaint_chart(aspects)

    st.subheader("Complaints hidden in 4–5★ reviews", anchor=False)
    st.caption("A high rating can still come with a warning. These sentences come from reviews that gave 4 or 5 stars.")
    options = aspects.loc[aspects["reviews_complaining"] > 0, "aspect"].head(TOP_ASPECTS).tolist()
    if not options:
        st.info("Nothing to show for this product.", icon=":material/info:")
        return
    aspect = st.pills("Aspect", options, default=options[0], key=f"hidden_{family}", label_visibility="collapsed")
    if aspect is None:
        st.caption("Choose an aspect above.")
        return
    found = data.examples(family, aspect, min_rating=4, max_rating=5, limit=5)
    if found.empty:
        st.info(f"No 4–5★ review sentences about {aspect.lower()} were flagged as complaints.", icon=":material/info:")
    for row in found.itertuples():
        quote(row.sentence, f"{stars(row.rating)} · {row.review_date} · {row.source_site}")


def comparison(a, b):
    col_a, col_b = st.columns(2, gap="large")
    for family, col in ((a, col_a), (b, col_b)):
        col.subheader(family, anchor=False)
        headline_metrics(family, col)

    aspects_a, aspects_b = data.aspects(a), data.aspects(b)
    difference = biggest_aspect_difference(aspects_a, aspects_b)
    if difference:
        aspect, pa, pb = difference
        more, fewer = (a, b) if pa > pb else (b, a)
        insight(f"The biggest difference is <b>{aspect.lower()}</b>: {pct(max(pa, pb), 2)} of {more} reviews complain about it, "
                f"against {pct(min(pa, pb), 2)} for {fewer}.")
    else:
        insight("These two products have similar complaint levels on every aspect (no difference of 0.5 points or more).")

    st.subheader("Complaints side by side", anchor=False)
    st.caption("Share of each product's reviews with a complaint about the aspect.")
    top = list(dict.fromkeys(aspects_a["aspect"].head(TOP_ASPECTS).tolist() + aspects_b["aspect"].head(TOP_ASPECTS).tolist()))
    va = dict(zip(aspects_a["aspect"], aspects_a["pct_reviews_complaining"]))
    vb = dict(zip(aspects_b["aspect"], aspects_b["pct_reviews_complaining"]))
    top = sorted(top, key=lambda x: max(va.get(x, 0), vb.get(x, 0)))
    fig = go.Figure()
    for family, values, colour in ((b, vb, GREY_DARK), (a, va, ACCENT)):
        fig.add_bar(name=family, y=top, x=[values.get(x, 0) for x in top], orientation="h", marker_color=colour,
                    hovertemplate=f"<b>{family}</b><br>%{{y}}: %{{x:.2f}}% of reviews<extra></extra>")
    fig.update_layout(barmode="group", legend=dict(traceorder="reversed"))
    fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor="#EEEBE4")
    fig.update_yaxes(showgrid=False)
    show(fig, height=80 + 46 * len(top))

    col_a, col_b = st.columns(2, gap="large")
    for family, col in ((a, col_a), (b, col_b)):
        with col:
            st.caption(f"Ratings · {family}")
            rating_chart(family)
