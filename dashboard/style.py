"""Visual style: colours, a Plotly chart template, and small reusable display pieces."""
import html

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ACCENT = "#1E5B57"       # the one accent colour: highlights what matters
ACCENT_SOFT = "#D7E6E3"
INK = "#1D1D1B"          # main text
INK_MUTED = "#6B6A65"    # secondary text
GREY = "#C9C5BA"         # neutral bars
GREY_DARK = "#8A877E"
RULE = "#E3E0D7"         # borders and grid lines

FONT = "Inter, 'Segoe UI', system-ui, sans-serif"

pio.templates["review_reality"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONT, size=13, color="#3C3A35"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[ACCENT, GREY_DARK, GREY, INK],
        margin=dict(l=8, r=16, t=8, b=8),
        # automargin: make room for long labels instead of cutting them off
        xaxis=dict(showgrid=False, zeroline=False, linecolor=RULE, ticks="", automargin=True,
                   title=dict(font=dict(color=INK_MUTED, size=12))),
        yaxis=dict(gridcolor="#EEEBE4", zeroline=False, ticks="", automargin=True,
                   title=dict(font=dict(color=INK_MUTED, size=12))),
        hoverlabel=dict(bgcolor="white", bordercolor=RULE, font=dict(family=FONT, size=12, color=INK)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None, font=dict(size=12)),
        bargap=0.35,
    )
)

CSS = f"""
<style>
.block-container {{ max-width: 1180px; padding-top: 4.25rem; }}
.rr-brand {{ font-family: 'Newsreader', Georgia, serif; font-size: 1.55rem; font-weight: 600; color: {INK}; line-height: 1.1; }}
.rr-tagline {{ color: {INK_MUTED}; font-size: 0.9rem; margin-top: 0.15rem; }}
.rr-note {{ color: {INK_MUTED}; font-size: 0.8rem; text-align: right; line-height: 1.5; }}
.rr-eyebrow {{ color: {ACCENT}; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.2rem; }}
.rr-lead {{ color: #3C3A35; font-size: 1.02rem; max-width: 46rem; line-height: 1.6; }}
.rr-quote {{ border-left: 2px solid {ACCENT}; padding: 0.15rem 0 0.15rem 0.9rem; margin: 0 0 0.9rem 0; }}
.rr-quote-text {{ color: {INK}; font-size: 0.95rem; line-height: 1.55; }}
.rr-meta {{ color: {INK_MUTED}; font-size: 0.78rem; margin-top: 0.2rem; }}
.rr-insight {{ background: {ACCENT_SOFT}33; border: 1px solid {RULE}; border-radius: 0.5rem; padding: 0.9rem 1.1rem; color: {INK}; line-height: 1.55; }}
.rr-insight b {{ color: {ACCENT}; }}
@media (max-width: 640px) {{ .rr-note {{ text-align: left; margin-top: 0.5rem; }} }}
</style>
"""


def apply_css():
    st.html(CSS)


def heading(eyebrow, title, lead=None):
    """Page heading: small coloured label, serif title, optional one-paragraph intro."""
    st.html(f'<div class="rr-eyebrow">{html.escape(eyebrow)}</div>')
    st.header(title, anchor=False)
    if lead:
        st.html(f'<p class="rr-lead">{lead}</p>')


def insight(text_html):
    """A highlighted, calculated finding. Pass already-escaped HTML."""
    st.html(f'<div class="rr-insight">{text_html}</div>')


def quote(sentence, meta):
    st.html(
        f'<div class="rr-quote"><div class="rr-quote-text">“{html.escape(sentence)}”</div>'
        f'<div class="rr-meta">{html.escape(meta)}</div></div>'
    )


def stars(rating):
    return f"{int(rating)}★"


def pct(value, digits=1):
    return "–" if value is None or value != value else f"{value:.{digits}f}%"


PAGE_BG = "#FAF9F6"


def show(fig, height=320):
    """Render a Plotly figure with our template and without the toolbar."""
    # Paint the chart with the page colour so no grey box appears behind it.
    fig.update_layout(template="review_reality", height=height, paper_bgcolor=PAGE_BG, plot_bgcolor=PAGE_BG)
    st.plotly_chart(fig, theme=None, width="stretch", config={"displayModeBar": False})


def table_height(rows):
    """Height that shows every row of a st.dataframe without an inner scrollbar (up to 15 rows)."""
    return 35 * (min(rows, 15) + 1) + 3
