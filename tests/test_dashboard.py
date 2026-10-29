"""Run every dashboard page headlessly (no browser) and check it renders without errors.

These tests need the real database (python -m review_reality.build); they are skipped if it is missing.
"""
import pytest
from streamlit.testing.v1 import AppTest

from review_reality.paths import DB_PATH, ROOT

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="database not built")
TIMEOUT = 120


def page_script(module_name):
    """A tiny script that applies the style and renders one page module."""
    import importlib

    from dashboard.style import apply_css

    apply_css()
    importlib.import_module(f"dashboard.{module_name}").render()


def run_page(module_name):
    at = AppTest.from_function(page_script, args=(module_name,), default_timeout=TIMEOUT)
    return at.run()


def assert_clean(at):
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.body for e in at.error]


def test_full_app_starts_on_overview():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=TIMEOUT).run()
    assert_clean(at)
    labels = [m.label for m in at.metric]
    assert "Unique reviews analysed" in labels


@pytest.mark.parametrize("module_name", ["overview", "shopper", "seller", "patterns", "method"])
def test_every_page_renders(module_name):
    assert_clean(run_page(module_name))


def test_shopper_every_product_and_compare_mode():
    at = run_page("shopper")
    for product in at.selectbox(key="shopper_product").options:
        at.selectbox(key="shopper_product").select(product).run()
        assert_clean(at)
    options = at.selectbox(key="shopper_compare").options
    at.selectbox(key="shopper_compare").select(options[1]).run()
    assert_clean(at)
    assert len(at.metric) == 8  # four metrics for each of the two products


def test_seller_every_product_and_rating_filters():
    at = run_page("seller")
    for product in at.selectbox(key="seller_product").options:
        at.selectbox(key="seller_product").select(product).run()
        assert_clean(at)
    for choice in ["1–2★", "3★", "4–5★", "All ratings"]:
        at.segmented_control[0].set_value(choice).run()
        assert_clean(at)


def test_patterns_every_product():
    at = run_page("patterns")
    for product in at.selectbox(key="patterns_product").options:
        at.selectbox(key="patterns_product").select(product).run()
        assert_clean(at)


def test_app_explains_what_to_do_when_database_is_missing(tmp_path, monkeypatch):
    def script():
        from unittest import mock

        import streamlit as st

        from dashboard import data

        with mock.patch.object(data, "database_ready", return_value=False):
            if not data.database_ready():
                st.subheader("The review database has not been built yet")

    at = AppTest.from_function(script).run()
    assert_clean(at)
    assert at.subheader[0].value == "The review database has not been built yet"
