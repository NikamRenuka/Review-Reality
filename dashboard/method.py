"""Data & method: where the data came from, what was done to it, and how far each number can be trusted."""
import plotly.graph_objects as go
import streamlit as st

from dashboard import data
from dashboard.style import ACCENT, GREY, heading, show

METRIC_LABELS = {
    "balanced_accuracy": ("Balanced accuracy", "Average of how well it spots negative and positive reviews. 0.5 = guessing."),
    "negative_recall": ("Recall", "Share of truly negative reviews that the model found."),
    "negative_precision": ("Precision", "Share of reviews the model called negative that really were negative."),
    "negative_f1": ("F1 score", "One number combining precision and recall for negative reviews."),
}


def render():
    heading("Data & method", "How the numbers are made",
            "Every figure in this dashboard is calculated from the dataset below by code in this project's repository.")

    st.subheader("The data", anchor=False)
    st.markdown(
        "- **Source:** [Consumer Reviews of Amazon Products](https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products) "
        "by Datafiniti, licensed **CC BY-NC-SA 4.0** (non-commercial use with credit).\n"
        "- **What it covers:** reviews of Amazon-made devices (Fire tablets, Kindle, Echo, Fire TV, AmazonBasics batteries) "
        "collected mostly from Best Buy and Amazon, 2009–2019.\n"
        "- **What it lacks:** verified-purchase flags, prices, seller data, and any labels saying whether a review is genuine."
    )

    steps = data.table("build_steps")
    st.subheader("From raw rows to unique reviews", anchor=False)
    st.caption("The same review was attached to every colour/size listing and repeated across three snapshot files, "
               "so copies were removed before any counting.")
    fig = go.Figure(go.Bar(x=steps["rows"], y=steps["step"], orientation="h",
                           marker_color=[GREY] * (len(steps) - 1) + [ACCENT],
                           text=[f"{r:,}" for r in steps["rows"]], textposition="inside", insidetextanchor="end",
                           textfont=dict(color="white"), hovertemplate="%{y}: %{x:,}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(visible=False)
    show(fig, height=170)

    st.subheader("How complaints are found", anchor=False)
    st.markdown(
        f"1. Each review is split into sentences.\n"
        f"2. **Keyword rules** tag sentences with product aspects (battery life, leaking, speed, screen…). "
        f"The keywords came from words that appear far more often in 1–2★ reviews than in 4–5★ reviews.\n"
        f"3. A **text model** (TF-IDF + logistic regression, trained on the star ratings) scores how negative each sentence sounds.\n"
        f"4. A sentence is counted as a **complaint** when the model is at least {int(data.COMPLAINT_THRESHOLD * 100)}% sure it is negative."
    )

    metrics = data.table("model_metrics").set_index("metric")["value"]
    st.caption(f"Model test on {int(metrics['test_reviews']):,} reviews it never saw during training "
               f"({int(metrics['test_negative_reviews'])} of them negative). Baseline = always guessing 'positive'.")
    cols = st.columns(len(METRIC_LABELS))
    for col, (key, (label, explanation)) in zip(cols, METRIC_LABELS.items()):
        baseline = metrics.get(f"baseline_{key}")
        col.metric(label, f"{metrics[key]:.2f}", border=True, help=explanation,
                   delta=f"{metrics[key] - baseline:+.2f} vs baseline" if baseline is not None else None,
                   delta_color="off")
    st.markdown(
        "**Hand check:** 50 randomly chosen flagged sentences were read; **38 of 50 (76%)** were real complaints about the "
        "tagged aspect. So complaint figures are **estimates**. They are most useful for comparing products and aspects "
        "measured the same way, and the dashboard always shows the sentences behind them."
    )

    st.subheader("Limits to keep in mind", anchor=False)
    st.markdown(
        "- **No proof of fake reviews.** Bursts and near-identical texts are patterns worth reading, nothing more.\n"
        "- **Reviewer names are not people.** Many different people share display names such as \"Amazon Customer\", "
        "so the dashboard does not rank reviewers.\n"
        "- **Old and narrow data.** Reviews end in March 2019 and cover about 20 Amazon product families.\n"
        "- **Few negative reviews.** 70% of reviews give 5 stars, so some products have only a few dozen negative reviews.\n"
        "- **Keyword rules miss some wording** and the text model sometimes misreads praise such as "
        "\"I worried it would lag, but it didn't\"."
    )
    st.caption("Full details: docs/METHODOLOGY.md and docs/DATASET.md in the project repository.")
